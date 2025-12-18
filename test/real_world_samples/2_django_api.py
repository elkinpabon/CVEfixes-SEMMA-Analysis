from django.http import JsonResponse
from django.views import View
import subprocess
import os

class ReportGenerator(View):
    def post(self, request):
        report_type = request.POST.get('type', 'pdf')
        filename = request.POST.get('filename', 'report')
        
        report_path = self.generate_report(filename, report_type)
        return JsonResponse({'path': report_path})
    
    def generate_report(self, filename, report_type):
        cmd = self.build_command(filename, report_type)
        
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = result.communicate()[0]
        return output.decode()
    
    def build_command(self, filename, rtype):
        converters = {
            'pdf': f'libreoffice --convert-to pdf {filename}',
            'doc': f'pandoc {filename} -o {filename}.docx',
            'html': f'markdown {filename} > {filename}.html',
        }
        return converters.get(rtype, f'file {filename}')

class SystemMonitor(View):
    def get(self, request):
        process = request.GET.get('process', 'python')
        cmd = f"ps aux | grep {process}"
        result = os.popen(cmd).read()
        
        return JsonResponse({'processes': result})
