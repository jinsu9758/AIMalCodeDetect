from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponse, FileResponse, Http404
import os
from django.conf import settings
import boto3

s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)


# 파일 다운로드 기능 구현
def file_download_view(request):
    s3_bucket = settings.AWS_STORAGE_FORE_BUCKET_NAME

    try:
        response = s3.list_objects_v2(Bucket=s3_bucket)

        if 'Contents' not in response:
            request.session['error'] = "S3 버킷에 파일이 없습니다."
            return redirect('index')

        files = response['Contents']
        file_count = len(files)

        if file_count == 0:
            request.session['error'] = "S3 버킷에 파일이 없습니다."
            return redirect('index')

        # 파일이 1개인 경우 다운로드 처리
        elif file_count == 1:
            s3_key = files[0]['Key']
            try:
                s3_file = s3.get_object(Bucket=s3_bucket, Key=s3_key)
                file_name = os.path.basename(s3_key)

                response = FileResponse(s3_file['Body'])
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response

            except s3.exceptions.NoSuchKey:
                request.session['error'] = "해당 파일을 찾을 수 없습니다."
                return redirect('index')
        else:
            request.session['error'] = f"S3 버킷에 파일이 {file_count}개 있어서 다운로드할 수 없습니다."
            return redirect('index')

    except Exception as e:
        request.session['error'] = f"S3에서 파일을 불러오는 중 오류가 발생했습니다: {str(e)}"
        return redirect('index')



def index(request):
    error_message = request.session.pop('error', None)  # 세션에서 error 메시지를 가져오고 삭제
    return render(request, 'index.html', {'error': error_message})
