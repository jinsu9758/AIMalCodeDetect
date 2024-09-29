from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import MaliciousResult
from .forms import FileUploadForm
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import boto3
import json

# aws s3 연결
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# 버킷 이름을 인자로 받아 안에 있는 모든 파일 데이터 삭제
def delete_files_bucket(bucket):
    s3_bucket = bucket

    try:
        response = s3.list_objects_v2(Bucket=s3_bucket)

        if 'Contents' not in response:
            print("S3 버킷에 삭제할 파일이 없습니다.")
            return

        # 삭제할 객체의 Key 리스트 생성
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]

        # 객체 삭제 요청
        delete_response = s3.delete_objects(
            Bucket=s3_bucket,
            Delete={
                'Objects': objects_to_delete
            }
        )

        print(f"{len(objects_to_delete)}개의 파일이 삭제되었습니다.")


    except Exception as e:
        print(f"S3 버킷에서 파일을 삭제하는 중 오류가 발생했습니다: {str(e)}")


# 파일 업로드 기능 → 업로드 여부에 따라서 alert 발생
@csrf_exempt
def file_upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            valid_extension = ['.acm', '.ax', '.cpl', '.dll', '.drv', '.efi', '.exe', '.mui', '.ocx', '.scr', '.sys', '.tsp']

            if file_extension in valid_extension:
                try:
                    # 파일 업로드 시, pre_bucket 안에 파일 삭제 후 파일 업로드
                    delete_files_bucket(settings.AWS_STORAGE_PRE_BUCKET_NAME)
                    s3.upload_fileobj(uploaded_file, settings.AWS_STORAGE_PRE_BUCKET_NAME, uploaded_file.name)
                    request.session['message'] = "정상적으로 업로드 되었습니다!"
                    return redirect('admin_page')

                except Exception as e:
                    request.session['message'] = f"S3 업로드 오류: {str(e)}"
                    return redirect('admin_page')
            else:
                request.session['message'] = "PE파일만 업로드할 수 있습니다."
                return redirect('admin_page')

    else:
        form = FileUploadForm()


# api를 이용해 파일에 대한 AI 결과값을 받음.
@csrf_exempt
def recieve_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mal_rate = data.get('mal_rate')
            filename = data.get('filename')
            
            # 결과 값을 받으면 로컬 sqlitedb에 해당 데이터를 저장
            if mal_rate is not None and filename is not None:
                MaliciousResult.objects.all().delete()
                result = MaliciousResult.objects.create(filename=filename, mal_rate=mal_rate)
                
                pre_bucket = settings.AWS_STORAGE_PRE_BUCKET_NAME
                fore_bucket = settings.AWS_STORAGE_FORE_BUCKET_NAME
                
                # 결과 값의 mal_rate를 검사했을때 정상 파일이면, fore_bucket에다가 파일 옮기기
                if mal_rate >=60: # 악성 파일
                    pass
                else: # 정상 파일
                    try:
                        delete_files_bucket(fore_bucket)
                        copy_source = {
                            'Bucket': pre_bucket,
                            'Key': filename
                        }
                        s3.copy(copy_source, fore_bucket, filename)
                        delete_files_bucket(pre_bucket)
                        return JsonResponse({'message': 'File moved successfully.'})
                    except Exception as e:
                        return JsonResponse({'error': str(e)}, status=500)


                return JsonResponse({'status': 'success', 'id': result.id}, status=201)
            else:
                return JsonResponse({'error': 'mal_rate not provided'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# admin_page의 chart.js를 위한 데이터 전송 / AI 탐지 결과물의 시각화
def get_chart_data(request):
    data = MaliciousResult.objects.values('check_time', 'filename', 'mal_rate')

    if data.exists():
        item = data.first()  # 첫 번째 항목 가져오기
        mal_rate = item['mal_rate']
        filename = item['filename']  # filename 가져오기
        
        chart_data = {
            'labels': ['Malware Detected', 'Non-Malware Detected'],  # 각 항목에 대한 레이블
            'datasets': [{
                'data': [mal_rate, 100 - mal_rate],  # 악성 비율과 정상 비율 데이터
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',  # 악성 비율 색상
                    'rgba(54, 162, 235, 0.2)',  # 정상 비율 색상
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                ],
                'borderWidth': 1,  # 테두리 두께
            }],
            'options': {
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{filename} AI 분석 결과'  # filename을 제목으로 사용
                    }
                }
            }
        }

    return JsonResponse(chart_data)



# 시각화한 결과물을 초기화(삭제) 시키기
@csrf_exempt
def reset_result(request):
    if request.method == 'GET':
        MaliciousResult.objects.all().delete()
        return redirect('admin_page') 
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# admin_page 로드
@csrf_exempt
def admin_page(request):
    form = FileUploadForm()
    message = request.session.pop('message', None)
    return render(request, 'admin_page.html', {'form': form, 'message': message})
