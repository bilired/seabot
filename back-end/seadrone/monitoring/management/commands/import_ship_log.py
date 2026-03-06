import re
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError

from monitoring.models import NutrientData, WaterQualityData
from monitoring.ship_gateway import parse_nutrient_payload, parse_packets, parse_water_payload


def parse_log_line(line: str):
    pattern = r'\[(.*?)\]\s*-\s*(.*?)\s*收到原始数据：(.*)'
    match = re.match(pattern, line)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None


def parse_time(value: str):
    dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return dt.replace(tzinfo=timezone.utc)


class Command(BaseCommand):
    help = '从连接服务日志回灌水质/营养盐数据到 Django 数据库'

    def add_arguments(self, parser):
        parser.add_argument('log_file', type=str, help='日志文件路径')

    def handle(self, *args, **options):
        log_file = options['log_file']
        try:
            with open(log_file, 'r', encoding='utf-8') as fp:
                lines = fp.readlines()
        except FileNotFoundError as exc:
            raise CommandError(f'日志文件不存在: {log_file}') from exc

        saved_water = 0
        saved_nutrient = 0

        for line in lines:
            ts_text, port_text, payload_hex = parse_log_line(line.strip())
            if not ts_text:
                continue

            try:
                packets, _ = parse_packets(bytes.fromhex(payload_hex))
            except Exception:
                continue

            for packet in packets:
                packet_type = packet['packet_type']
                try:
                    if packet_type == 'W':
                        model_data = parse_water_payload(port_text, packet['payload_text'])
                        obj = WaterQualityData.objects.create(**model_data)
                        obj.collection_time = parse_time(ts_text)
                        obj.save(update_fields=['collection_time'])
                        saved_water += 1
                    elif packet_type in ('Y', '@'):
                        model_data = parse_nutrient_payload(port_text, packet['payload_text'])
                        obj = NutrientData.objects.create(**model_data)
                        obj.collection_time = parse_time(ts_text)
                        obj.save(update_fields=['collection_time'])
                        saved_nutrient += 1
                except Exception:
                    continue

        self.stdout.write(self.style.SUCCESS(
            f'导入完成: water={saved_water}, nutrient={saved_nutrient}'
        ))
