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



# 파일 분석 기능 → 업로드 여부에 따라서 alert 발생
@csrf_exempt
def file_analysis_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            valid_extension = ['.zip', '.acm', '.ax', '.cpl', '.dll', '.drv', '.efi', '.exe', '.mui', '.ocx', '.scr', '.sys', '.tsp']

            if file_extension in valid_extension:
                try:
                    # 파일 업로드 시, pre_bucket 안에 파일 삭제 후 파일 업로드
                    delete_files_bucket(settings.AWS_STORAGE_PRE_BUCKET_NAME)
                    s3.upload_fileobj(uploaded_file, settings.AWS_STORAGE_PRE_BUCKET_NAME, uploaded_file.name)
                    request.session['message'] = "잠시후에 새로고침을 해주세요"
                    return redirect('developer_page')

                except Exception as e:
                    request.session['message'] = f"S3 업로드 오류: {str(e)}"
                    return redirect('developer_page')
            else:
                request.session['message'] = "ZIP파일 또는 PE파일만 업로드할 수 있습니다."
                return redirect('developer_page')

    else:
        form = FileUploadForm()



# api를 이용해 파일에 대한 AI 결과값을 받음.
@csrf_exempt
def recieve_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            success_data = data.get('success', {})
            fail_data = data.get('fail', [])

            # 기존 데이터 삭제
            MaliciousResult.objects.all().delete()
            
            # 성공한 파일 데이터를 저장
            for filename, mal_rate in success_data.items():
                if mal_rate is not None and filename:
                    MaliciousResult.objects.create(
                        filename=filename,
                        mal_rate=mal_rate * 100,
                        is_success=True
                    )

            # 실패한 파일 데이터를 저장
            for filename in fail_data:
                MaliciousResult.objects.create(
                    filename=filename,
                    mal_rate=None,  # 실패한 파일이므로 mal_rate는 없음
                    is_success=False
                )

            return JsonResponse({'status': 'success'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def confirm_upload_view(request):
    if request.method == "POST":
        try:
            # JavaScript에서 보낸 JSON 데이터를 파싱
            data = json.loads(request.body)
            files = data.get('files')  # 여러 파일 정보가 담긴 리스트

            if files is not None:
                for file_data in files:
                    mal_rate = file_data.get('malRate')
                    filename = file_data.get('filename')

                    if mal_rate is None:
                        return JsonResponse({'success': False, 'error': f'{filename}: mal_rate is missing'})

                    # mal_rate가 90 이상인 파일이 하나라도 있으면 업로드를 차단
                    if mal_rate >= 70:
                        return JsonResponse({'success': False, 'error': f'{filename}: mal_rate is too high'})

                # 모든 파일이 업로드 가능한 상태일 때만 업로드 처리
                return handle_file_upload(request)  # 다중 파일 업로드 처리 함수 호출
            else:
                return JsonResponse({'success': False, 'error': 'No files provided'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# 파일 업로드 로직 처리 함수
def handle_file_upload(request):
    try:
        pre_bucket = settings.AWS_STORAGE_PRE_BUCKET_NAME
        fore_bucket = settings.AWS_STORAGE_FORE_BUCKET_NAME

        # pre_bucket의 모든 파일을 가져옴
        objects = s3.list_objects_v2(Bucket=pre_bucket)
        delete_files_bucket(fore_bucket)
        if 'Contents' in objects:
            # 각 파일을 fore_bucket으로 복사
            for obj in objects['Contents']:
                filename = obj['Key']
                copy_source = {
                    'Bucket': pre_bucket,
                    'Key': filename
                }

                # 파일을 fore_bucket으로 복사
                s3.copy(copy_source, fore_bucket, filename)

        else:
            return JsonResponse({'success': False, 'error': 'No files found in the pre_bucket'})

        return JsonResponse({'success': True, 'message': 'All files have been copied successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    


def get_chart_data(request):
    # is_success가 True인 데이터 필터링
    data = MaliciousResult.objects.filter(is_success=True).values('check_time', 'filename', 'mal_rate')

    if data.exists():
        chart_data = {
            'labels': [],  # 각 파일의 레이블 (파일 이름)
            'datasets': [
                {  # 악성 비율 데이터셋
                    'label': 'Malware Detected',
                    'data': [],  # 파일별 악성 비율 데이터
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1,
                    'stack': 'Stack 0',  # 스택 그룹 지정
                },
                {  # 정상 비율 데이터셋
                    'label': 'Non-Malware Detected',
                    'data': [],  # 파일별 정상 비율 데이터
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1,
                    'stack': 'Stack 0',  # 동일한 스택 그룹
                }
            ],
            'options': {
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'AI 분석 결과'  # 제목
                    }
                },
                'scales': {
                    'x': {
                        'stacked': True  # X축에서 스택 활성화
                    },
                    'y': {
                        'stacked': True  # Y축에서 스택 활성화
                    }
                }
            }
        }

        # 각 항목에 대해 반복하며 데이터를 추가
        for item in data:
            mal_rate = item['mal_rate']
            filename = item['filename']

            # 파일 이름을 레이블로 추가
            chart_data['labels'].append(f'{filename}')

            # 악성 비율 데이터를 추가
            chart_data['datasets'][0]['data'].append(mal_rate)

            # 정상 비율 데이터를 추가 (100에서 악성 비율을 뺀 값)
            chart_data['datasets'][1]['data'].append(100 - mal_rate)
        
        return JsonResponse(chart_data)
    else:
        # 성공한 데이터가 없을 경우
        chart_data = {}
        return JsonResponse(chart_data)


def get_table_data(request):
    # 전체 데이터를 가져옴 (필요에 따라 성공/실패 데이터로 나눌 수 있음)
    success_data = MaliciousResult.objects.filter(is_success=True).values('check_time', 'filename', 'mal_rate')
    fail_data = MaliciousResult.objects.filter(is_success=False).values('check_time', 'filename', 'mal_rate')

    table_data = {
        'success': list(success_data),
        'fail': list(fail_data)
    }
    return JsonResponse(table_data)


# 시각화한 결과물을 초기화(삭제) 시키기
@csrf_exempt
def reset_result(request):
    if request.method == 'GET':
        MaliciousResult.objects.all().delete()
        return redirect('developer_page') 
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



# developer_page 로드
@csrf_exempt
def developer_page(request):
    if request.user.is_authenticated is False:
        return redirect('/')
    if request.user.is_uploader is False:
        return redirect('/')
    form = FileUploadForm()
    message = request.session.pop('message', None)
    return render(request, 'developer_page.html', {'form': form, 'message': message})