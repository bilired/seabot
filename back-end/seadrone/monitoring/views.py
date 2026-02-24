from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import WaterQualityData, NutrientData


@api_view(['GET'])
@permission_classes([])
def get_water_quality_data(request):
    """获取水质监测数据
    
    返回：水质数据列表
    """
    try:
        # 获取最新的20条数据
        water_data = WaterQualityData.objects.all()[:20]
        
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
                "warningCode": item.warning_code,
                "collectionTime": item.collection_time.strftime('%Y-%m-%d %H:%M:%S'),
                "connectionStatus": item.connection_status
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
        # 获取最新的20条数据
        nutrient_data = NutrientData.objects.all()[:20]
        
        data_list = []
        for item in nutrient_data:
            data_list.append({
                "shipModel": item.ship_model,
                "phosphate": item.phosphate,
                "phosphateTime": item.phosphate_time.strftime('%Y-%m-%d %H:%M:%S'),
                "ammonia": item.ammonia,
                "ammoniaTime": item.ammonia_time.strftime('%Y-%m-%d %H:%M:%S'),
                "nitrate": item.nitrate,
                "nitrateTime": item.nitrate_time.strftime('%Y-%m-%d %H:%M:%S'),
                "nitrite": item.nitrite,
                "nitriteTime": item.nitrite_time.strftime('%Y-%m-%d %H:%M:%S'),
                "errorCode1": item.error_code1,
                "errorCode2": item.error_code2,
                "instrumentStatus": item.instrument_status,
                "collectionTime": item.collection_time.strftime('%Y-%m-%d %H:%M:%S'),
                "connectionStatus": item.connection_status
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
        from django.utils import timezone
        
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
