from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .forms import FileUploadForm
from .models import FileUpload
from django.views.decorators.csrf import csrf_exempt
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


def delete_files_fore_bucket():
    s3_bucket = settings.AWS_STORAGE_FORE_BUCKET_NAME

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



# Create your views here.
# s3로 업로드하도록 수정 필요.
@csrf_exempt
def file_upload_view(request):
    message = None

    if 'message' in request.session:
        message = request.session['message']
        del request.session['message']

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            valid_extension = ['.acm', '.ax', '.cpl', '.dll', '.drv', '.efi', '.exe', '.mui', '.ocx', '.scr', '.sys', '.tsp']

            if file_extension in valid_extension:
                # AWS S3에 파일 업로드
                try:
                    # 기존 버킷 내 파일 삭제 로직 (나중에 코드 삭제해야함.)
                    delete_files_fore_bucket()
                    # S3 버킷에 파일 업로드 버킷 이름 수정해야함.
                    s3.upload_fileobj(uploaded_file, settings.AWS_STORAGE_FORE_BUCKET_NAME, uploaded_file.name)
                    request.session['message'] = "정상적으로 업로드 되었습니다!"
                    return redirect('file_upload')

                except Exception as e:
                    request.session['message'] = f"S3 업로드 오류: {str(e)}"
                    return redirect('file_upload')
            else:
                request.session['message'] = "PE파일만 업로드할 수 있습니다."
                return redirect('file_upload')

    else:
        form = FileUploadForm()

    return render(request, 'fileupload.html', {'form': form, 'message': message})


# 파일 다운로드 뷰
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

        elif file_count == 1:
            # 파일이 1개인 경우 다운로드 처리
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
