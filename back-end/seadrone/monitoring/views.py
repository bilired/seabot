from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, timedelta

from django.utils import timezone
from .models import BoatTrackRecord, WaterQualityData, NutrientData, VideoStreamTransferRecord
from .ship_gateway import (
    gateway_service,
    parse_packets,
    parse_water_payload,
    parse_nutrient_payload,
    parse_boat_payload,
    parse_depth_payload,
    parse_rtk_payload,
)


def _parse_payload_timestamp(value):
    if value in (None, ''):
        return None

    text = str(value).strip()
    for fmt in ('%Y%m%d%H%M%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S'):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    try:
        epoch = float(text)
        if epoch > 10_000_000_000:
            epoch /= 1000.0
        return datetime.fromtimestamp(epoch, tz=timezone.utc)
    except ValueError:
        return None


@api_view(['GET'])
@permission_classes([])
def get_water_quality_data(request):
    """获取水质监测数据
    
    返回：水质数据列表
    """
    try:
        # 获取最新的100条数据
        water_data = WaterQualityData.objects.all()[:200]
        
        data_list = []
        for item in water_data:
            data_list.append({
                "ship_model": item.ship_model,
                "timestamp": timezone.localtime(item.timestamp or item.collection_time).strftime('%Y-%m-%d %H:%M:%S'),
                "warn": item.warn,
                "temperature": item.temperature,
                "pH": item.pH,
                "chlorophyll": item.chlorophyll,
                "salinity": item.salinity,
                "dissolved_oxygen": item.dissolved_oxygen,
                "conductivity": item.conductivity,
                "turbidity": item.turbidity,
                "blue-green": item.blue_green
            })
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": data_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取水质数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_nutrient_data(request):
    """获取营养盐数据
    
    返回：营养盐数据列表
    """
    try:
        # 获取最新的200条数据
        nutrient_data = NutrientData.objects.all()[:200]
        
        data_list = []
        for item in nutrient_data:
            data_list.append({
                "data_id": item.ship_model,
                "timestamp": timezone.localtime(item.timestamp).strftime('%Y-%m-%d %H:%M:%S') if item.timestamp else None,
                "status": item.status,
                "ammonia_nitrogen": item.ammonia_nitrogen,
                "ammonia_nitrogen_timestamp": timezone.localtime(item.ammonia_nitrogen_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "nitrate": item.nitrate,
                "nitrate_timestamp": timezone.localtime(item.nitrate_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "sub_nitrate": item.sub_nitrate,
                "sub_nitrate_timestamp": timezone.localtime(item.sub_nitrate_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "phosphates": item.phosphates,
                "phosphates_timestamp": timezone.localtime(item.phosphates_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "warn": item.warn,
            })
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": data_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取营养盐数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 允许设备无需认证上传
def upload_water_quality_data(request):
    """无人船上传水质数据
    
    参数：
    - ship_model: 船型号
    - temperature: 水温
    - ... 其他水质参数
    """
    try:
        ship_model = request.data.get('ship_model')
        timestamp = request.data.get('timestamp')
        warn = request.data.get('warn', '0')
        temperature = request.data.get('temperature')
        pH = request.data.get('pH')
        chlorophyll = request.data.get('chlorophyll')
        salinity = request.data.get('salinity')
        dissolved_oxygen = request.data.get('dissolved_oxygen')
        conductivity = request.data.get('conductivity')
        turbidity = request.data.get('turbidity')
        blue_green = request.data.get('blue-green')

        if not all([ship_model, temperature is not None, pH is not None]):
            return Response({
                "code": 400,
                "msg": "缺少必填参数"
            }, status=status.HTTP_200_OK)

        water_data = WaterQualityData.objects.create(
            ship_model=ship_model,
            timestamp=_parse_payload_timestamp(timestamp),
            temperature=float(temperature),
            pH=float(pH),
            chlorophyll=float(chlorophyll) if chlorophyll else 0,
            salinity=float(salinity) if salinity else 0,
            dissolved_oxygen=float(dissolved_oxygen) if dissolved_oxygen else 0,
            conductivity=float(conductivity) if conductivity else 0,
            turbidity=float(turbidity) if turbidity else 0,
            blue_green=float(blue_green) if blue_green else 0,
            warn=str(warn) if warn is not None else '0'
        )

        return Response({
            "code": 200,
            "msg": "数据上传成功",
            "data": {
                "id": water_data.id,
                "timestamp": (water_data.timestamp or water_data.collection_time).isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"上传失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 允许设备无需认证上传
def upload_nutrient_data(request):
    """无人船上传营养盐数据
    
    参数：
    - data_id: 数据唯一标识
    - phosphate: 磷酸盐
    - ... 其他营养盐参数
    """
    try:
        data_id = request.data.get('data_id')
        timestamp = request.data.get('timestamp')
        status_value = request.data.get('status', 0)
        ammonia_nitrogen = request.data.get('ammonia_nitrogen')
        ammonia_nitrogen_timestamp = request.data.get('ammonia_nitrogen_timestamp')
        nitrate = request.data.get('nitrate')
        nitrate_timestamp = request.data.get('nitrate_timestamp')
        sub_nitrate = request.data.get('sub_nitrate')
        sub_nitrate_timestamp = request.data.get('sub_nitrate_timestamp')
        phosphates = request.data.get('phosphates')
        phosphates_timestamp = request.data.get('phosphates_timestamp')
        warn = request.data.get('warn', '0')

        if not all([data_id, phosphates is not None]):
            return Response({
                "code": 400,
                "msg": "缺少必填参数"
            }, status=status.HTTP_200_OK)

        nutrient_data = NutrientData.objects.create(
            ship_model=str(data_id),
            timestamp=_parse_payload_timestamp(timestamp),
            status=int(status_value) if status_value is not None else 0,
            ammonia_nitrogen=float(ammonia_nitrogen) if ammonia_nitrogen else 0,
            ammonia_nitrogen_timestamp=_parse_payload_timestamp(ammonia_nitrogen_timestamp) or timezone.now(),
            nitrate=float(nitrate) if nitrate else 0,
            nitrate_timestamp=_parse_payload_timestamp(nitrate_timestamp) or timezone.now(),
            sub_nitrate=float(sub_nitrate) if sub_nitrate else 0,
            sub_nitrate_timestamp=_parse_payload_timestamp(sub_nitrate_timestamp) or timezone.now(),
            phosphates=float(phosphates),
            phosphates_timestamp=_parse_payload_timestamp(phosphates_timestamp) or timezone.now(),
            warn=str(warn) if warn is not None else '0',
        )

        return Response({
            "code": 200,
            "msg": "数据上传成功",
            "data": {
                "id": nutrient_data.id,
                "timestamp": (nutrient_data.timestamp or nutrient_data.collection_time).isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"上传失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_video_stream_data(request):
    """获取视频流传输记录"""
    try:
        records = VideoStreamTransferRecord.objects.all()[:200]
        data_list = []
        for item in records:
            data_list.append({
                "ship_model": item.ship_model,
                "timestamp": timezone.localtime(item.timestamp or item.collection_time).strftime('%Y-%m-%d %H:%M:%S'),
                "stream_protocol": item.stream_protocol,
                "video_codec": item.video_codec,
                "transport_protocol": item.transport_protocol,
                "source_ip": item.source_ip,
                "source_port": item.source_port,
                "target_ip": item.target_ip,
                "target_port": item.target_port,
                "stream_url": item.stream_url,
                "resolution": f"{item.frame_width}x{item.frame_height}" if item.frame_width and item.frame_height else "--",
                "fps": item.fps,
                "bitrate_kbps": item.bitrate_kbps,
                "packet_size": item.packet_size,
                "packet_count": item.packet_count,
                "frame_count": item.frame_count,
                "loss_rate": item.loss_rate,
                "latency_ms": item.latency_ms,
                "jitter_ms": item.jitter_ms,
                "status": item.status,
                "warn": item.warn,
            })

        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": data_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取视频流数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def upload_video_stream_data(request):
    """上传视频流传输记录（设备侧可直接调用）"""
    try:
        ship_model = (request.data.get('ship_model') or request.data.get('shipModel') or '').strip()
        timestamp = request.data.get('timestamp')

        if not ship_model:
            return Response({
                "code": 400,
                "msg": "缺少必填参数 ship_model"
            }, status=status.HTTP_200_OK)

        record = VideoStreamTransferRecord.objects.create(
            ship_model=ship_model,
            timestamp=_parse_payload_timestamp(timestamp),
            stream_protocol=str(request.data.get('stream_protocol') or request.data.get('streamProtocol') or 'RTSP').strip(),
            video_codec=str(request.data.get('video_codec') or request.data.get('videoCodec') or 'H265').strip(),
            transport_protocol=str(request.data.get('transport_protocol') or request.data.get('transportProtocol') or 'UDP').strip(),
            source_ip=str(request.data.get('source_ip') or request.data.get('sourceIp') or '').strip(),
            source_port=request.data.get('source_port') or request.data.get('sourcePort') or None,
            target_ip=str(request.data.get('target_ip') or request.data.get('targetIp') or '').strip(),
            target_port=request.data.get('target_port') or request.data.get('targetPort') or None,
            stream_url=str(request.data.get('stream_url') or request.data.get('streamUrl') or '').strip(),
            frame_width=request.data.get('frame_width') or request.data.get('frameWidth') or None,
            frame_height=request.data.get('frame_height') or request.data.get('frameHeight') or None,
            fps=request.data.get('fps') or None,
            bitrate_kbps=request.data.get('bitrate_kbps') or request.data.get('bitrateKbps') or None,
            packet_size=request.data.get('packet_size') or request.data.get('packetSize') or None,
            packet_count=request.data.get('packet_count') or request.data.get('packetCount') or 0,
            frame_count=request.data.get('frame_count') or request.data.get('frameCount') or 0,
            loss_rate=request.data.get('loss_rate') or request.data.get('lossRate') or 0,
            latency_ms=request.data.get('latency_ms') or request.data.get('latencyMs') or None,
            jitter_ms=request.data.get('jitter_ms') or request.data.get('jitterMs') or None,
            status=str(request.data.get('status') or 'normal').strip(),
            warn=str(request.data.get('warn') or '0').strip(),
            raw_payload=str(request.data.get('raw_payload') or request.data.get('rawPayload') or ''),
        )

        return Response({
            "code": 200,
            "msg": "视频流记录上传成功",
            "data": {
                "id": record.id,
                "timestamp": (record.timestamp or record.collection_time).isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"上传视频流记录失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def upload_ship_packet_data(request):
    """上传无人船原始十六进制报文并解析入库"""
    try:
        ship_port = int(request.data.get('shipPort', 0))
        packet_hex = (request.data.get('packetHex') or '').replace(' ', '')

        if not ship_port or not packet_hex:
            return Response({
                "code": 400,
                "msg": "缺少 shipPort 或 packetHex"
            }, status=status.HTTP_200_OK)

        packet_bytes = bytes.fromhex(packet_hex)
        packets, remaining = parse_packets(packet_bytes)

        saved = {
            'water': 0,
            'nutrient': 0,
            'boat': 0,
            'depth': 0,
            'rtk': 0,
        }

        for packet in packets:
            packet_type = packet['packet_type']
            if packet_type == 'W':
                model_data = parse_water_payload(str(ship_port), packet['payload_text'])
                WaterQualityData.objects.create(**model_data)
                saved['water'] += 1
            elif packet_type in ('Y', '@'):
                model_data = parse_nutrient_payload(str(ship_port), packet['payload_text'])
                NutrientData.objects.create(**model_data)
                saved['nutrient'] += 1
            elif packet_type == 'B':
                # Type-B is boat status/identity packet; parse for protocol validation.
                parse_boat_payload(packet['payload_text'])
                saved['boat'] += 1
            elif packet_type == 'D':
                parse_depth_payload(packet['payload_text'])
                saved['depth'] += 1
            elif packet_type == '0':
                parse_rtk_payload(packet['payload_text'])
                saved['rtk'] += 1

        return Response({
            "code": 200,
            "msg": "解析成功",
            "data": {
                "packetCount": len(packets),
                "remainingBytes": len(remaining),
                "saved": saved,
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            "code": 400,
            "msg": f"报文解析失败: {str(e)}"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"上传失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def ship_gateway_start(request):
    """启动TCP船舶网关服务"""
    try:
        gateway_service.start()
        return Response({
            "code": 200,
            "msg": "网关已启动",
            "data": gateway_service.status()
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"启动失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def ship_gateway_status(request):
    """查看TCP船舶网关服务状态"""
    return Response({
        "code": 200,
        "msg": "获取成功",
        "data": gateway_service.status()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
def device_locations(request):
    """返回所有设备的当前/最后已知位置及在线状态。

    在线设备：从 gateway 内存中实时取位置（online=true）。
    离线设备：从 BoatTrackRecord 中取最后一条有效坐标（online=false）。
    """
    gateway_data = gateway_service.status()
    last_boat_packets = gateway_data.get('last_boat_packets') or {}
    reported_models = gateway_data.get('reported_models') or {}

    # Build online set by ship_model for dedup later
    locations: dict[str, dict] = {}

    for port_str, packet in last_boat_packets.items():
        lat = packet.get('latitude')
        lng = packet.get('longitude')
        if lat is None or lng is None:
            continue

        model = (
            packet.get('ship_model')
            or reported_models.get(port_str)
            or f'船体-{port_str}'
        ).strip()

        # If same model reported on multiple ports, prefer the freshest entry —
        # we keep the first hit here since gateway already tracks latest packet.
        if model not in locations:
            locations[model] = {
                'ship_model': model,
                'latitude': lat,
                'longitude': lng,
                'course': packet.get('course'),
                'speed': packet.get('speed'),
                'battery_level': packet.get('battery_level'),
                'online': True,
                'source_port': port_str,
            }

    # Offline fallback: query DB for every distinct model not already online
    online_models = set(locations.keys())
    offline_models = (
        BoatTrackRecord.objects
        .exclude(ship_model__in=online_models)
        .values_list('ship_model', flat=True)
        .distinct()
    )

    for model in offline_models:
        if not model:
            continue
        last_rec = (
            BoatTrackRecord.objects
            .filter(ship_model=model, latitude__isnull=False, longitude__isnull=False)
            .order_by('-recorded_at')
            .first()
        )
        if last_rec:
            locations[model] = {
                'ship_model': model,
                'latitude': last_rec.latitude,
                'longitude': last_rec.longitude,
                'course': last_rec.course,
                'speed': last_rec.speed,
                'battery_level': last_rec.battery_level,
                'online': False,
                'recorded_at': timezone.localtime(last_rec.recorded_at).strftime('%Y-%m-%d %H:%M:%S'),
            }

    return Response({
        'code': 200,
        'msg': '获取成功',
        'data': list(locations.values()),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def ship_action(request):
    """发送无人船/遥控器控制命令"""
    try:
        cmd = request.data.get('cmd')
        ship_port = int(request.data.get('shipPort'))
        control_port = int(request.data.get('controlPort'))
    except Exception:
        return Response({
            "code": 400,
            "msg": "参数错误，示例: {\"cmd\":\"up\",\"shipPort\":9001,\"controlPort\":9002}"
        }, status=status.HTTP_200_OK)

    try:
        result = gateway_service.send_action(cmd=cmd, ship_port=ship_port, control_port=control_port)
        success = len(result['delivered_ports']) > 0
        return Response({
            "code": 200 if success else 503,
            "msg": "发送成功" if success else "设备未在线",
            "data": result
        }, status=status.HTTP_200_OK if success else status.HTTP_503_SERVICE_UNAVAILABLE)
    except ValueError as e:
        return Response({
            "code": 400,
            "msg": str(e)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"发送失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def ship_track_history(request):
    """查询船体轨迹历史记录（数据库持久化）"""
    try:
        ship_model = (request.query_params.get('ship_model') or '').strip()
        ship_port = request.query_params.get('shipPort')
        days = int(request.query_params.get('days', 7))
        days = max(1, min(days, 30))

        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')

        queryset = BoatTrackRecord.objects.all()
        if ship_model:
            queryset = queryset.filter(ship_model__iexact=ship_model)
        if ship_port not in (None, ''):
            queryset = queryset.filter(ship_port=int(ship_port))

        if start_date:
            start_dt = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            queryset = queryset.filter(recorded_at__gte=start_dt)
        if end_date:
            end_dt = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
            queryset = queryset.filter(recorded_at__lt=end_dt)

        if not start_date and not end_date:
            since = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(recorded_at__gte=since)

        records = queryset.order_by('recorded_at')[:10000]
        data = []
        for item in records:
            data.append({
                'id': item.id,
                'ship_model': item.ship_model,
                'shipPort': item.ship_port,
                'boatTimestamp': item.boat_timestamp,
                'deviceTime': timezone.localtime(item.device_time).strftime('%Y-%m-%d %H:%M:%S') if item.device_time else None,
                'latitude': item.latitude,
                'longitude': item.longitude,
                'course': item.course,
                'speed': item.speed,
                'battery_level': item.battery_level,
                'water_extraction': item.water_extraction,
                'recordedAt': timezone.localtime(item.recorded_at).strftime('%Y-%m-%d %H:%M:%S'),
            })

        return Response({
            'code': 200,
            'msg': '获取成功',
            'data': data,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'code': 500,
            'msg': f'获取轨迹失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
