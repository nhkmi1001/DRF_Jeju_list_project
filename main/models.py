from django.db import models

# Create your models here.

class Tags(models.Model):
    class meta:
        db_table = 'tags'
    tagname = models.TextField()
    
class Contents(models.Model):
    class meta:
        db_table = 'contents'
    content = models.TextField()
    
class Store(models.Model):
    store_id = models.CharField(max_length=100) # https://map.kakao.com/여기
    store_name = models.TextField() #상호명
    address = models.TextField() # 가게 주소
    star = models.TextField() # 가게 별점
    tags = models.ManyToManyField(Tags, related_name='stores')
    contents = models.ManyToManyField(Contents, related_name='contents') #리뷰 내용
    img = models.TextField(max_length=256, default='')

    class meta:
        db_table = 'store'