from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, timedelta

from django.utils import timezone
from .models import BoatTrackRecord, WaterQualityData, NutrientData
from .ship_gateway import (
    gateway_service,
    parse_packets,
    parse_water_payload,
    parse_nutrient_payload,
    parse_boat_payload,
    parse_depth_payload,
    parse_rtk_payload,
)


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
                "shipModel": item.ship_model,
                "temperature": item.temperature,
                "ph": item.ph,
                "chlorophyll": item.chlorophyll,
                "salinity": item.salinity,
                "dissolvedOxygen": item.dissolved_oxygen,
                "conductivity": item.conductivity,
                "turbidity": item.turbidity,
                "algae": item.algae,
                "collectionTime": timezone.localtime(item.collection_time).strftime('%Y-%m-%d %H:%M:%S')
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
                "shipModel": item.ship_model,
                "phosphate": item.phosphate,
                "phosphateTime": timezone.localtime(item.phosphate_time).strftime('%Y-%m-%d %H:%M:%S'),
                "ammonia": item.ammonia,
                "ammoniaTime": timezone.localtime(item.ammonia_time).strftime('%Y-%m-%d %H:%M:%S'),
                "nitrate": item.nitrate,
                "nitrateTime": timezone.localtime(item.nitrate_time).strftime('%Y-%m-%d %H:%M:%S'),
                "nitrite": item.nitrite,
                "nitriteTime": timezone.localtime(item.nitrite_time).strftime('%Y-%m-%d %H:%M:%S'),
                "collectionTime": timezone.localtime(item.collection_time).strftime('%Y-%m-%d %H:%M:%S')
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
    - shipModel: 船型号
    - temperature: 水温
    - ... 其他水质参数
    """
    try:
        ship_model = request.data.get('shipModel')
        temperature = request.data.get('temperature')
        ph = request.data.get('ph')
        chlorophyll = request.data.get('chlorophyll')
        salinity = request.data.get('salinity')
        dissolved_oxygen = request.data.get('dissolvedOxygen')
        conductivity = request.data.get('conductivity')
        turbidity = request.data.get('turbidity')
        algae = request.data.get('algae')
        warning_code = request.data.get('warningCode', '正常')

        if not all([ship_model, temperature is not None, ph is not None]):
            return Response({
                "code": 400,
                "msg": "缺少必填参数"
            }, status=status.HTTP_200_OK)

        water_data = WaterQualityData.objects.create(
            ship_model=ship_model,
            temperature=float(temperature),
            ph=float(ph),
            chlorophyll=float(chlorophyll) if chlorophyll else 0,
            salinity=float(salinity) if salinity else 0,
            dissolved_oxygen=float(dissolved_oxygen) if dissolved_oxygen else 0,
            conductivity=float(conductivity) if conductivity else 0,
            turbidity=float(turbidity) if turbidity else 0,
            algae=int(algae) if algae else 0,
            warning_code=warning_code
        )

        return Response({
            "code": 200,
            "msg": "数据上传成功",
            "data": {
                "id": water_data.id,
                "collectionTime": water_data.collection_time.isoformat()
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
    - shipModel: 船型号
    - phosphate: 磷酸盐
    - ... 其他营养盐参数
    """
    try:
        ship_model = request.data.get('shipModel')
        phosphate = request.data.get('phosphate')
        ammonia = request.data.get('ammonia')
        nitrate = request.data.get('nitrate')
        nitrite = request.data.get('nitrite')
        error_code1 = request.data.get('errorCode1', '00')
        error_code2 = request.data.get('errorCode2', '00')
        instrument_status = request.data.get('instrumentStatus', '正常')

        if not all([ship_model, phosphate is not None]):
            return Response({
                "code": 400,
                "msg": "缺少必填参数"
            }, status=status.HTTP_200_OK)

        now = timezone.now()
        nutrient_data = NutrientData.objects.create(
            ship_model=ship_model,
            phosphate=float(phosphate),
            phosphate_time=now,
            ammonia=float(ammonia) if ammonia else 0,
            ammonia_time=now,
            nitrate=float(nitrate) if nitrate else 0,
            nitrate_time=now,
            nitrite=float(nitrite) if nitrite else 0,
            nitrite_time=now,
            error_code1=error_code1,
            error_code2=error_code2,
            instrument_status=instrument_status
        )

        return Response({
            "code": 200,
            "msg": "数据上传成功",
            "data": {
                "id": nutrient_data.id,
                "collectionTime": nutrient_data.collection_time.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"上传失败: {str(e)}"
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
        ship_model = (request.query_params.get('shipModel') or '').strip()
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
                'shipModel': item.ship_model,
                'shipPort': item.ship_port,
                'boatTimestamp': item.boat_timestamp,
                'deviceTime': timezone.localtime(item.device_time).strftime('%Y-%m-%d %H:%M:%S') if item.device_time else None,
                'status': item.status,
                'latitude': item.latitude,
                'longitude': item.longitude,
                'speed': item.speed,
                'direction': item.direction,
                'batteryVoltage': item.battery_voltage,
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
