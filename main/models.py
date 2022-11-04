from django.db import models

# Create your models here.


    
class Store(models.Model):
    store_id = models.CharField(max_length=100) # https://map.kakao.com/여기
    store_name = models.TextField() #상호명
    address = models.TextField() # 가게 주소
    star = models.TextField() # 가게 별점
    img = models.TextField(max_length=256, default='')

    class meta:
        db_table = 'store'

class Tags(models.Model):
    class meta:
        db_table = 'tags'
    name = models.CharField(max_length=256)
    
class Reviews(models.Model):
    class meta:
        db_table = 'review'
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    content = models.TextField()
    tag = models.ManyToManyField(Tags, related_name='review')