# sdk

## java-client
see more info in `RecClientTest`  
### push doc
eg: 
```java
ItemReq itemReq = new ItemReq();
itemReq.setCmd(PushCmd.INSERT);
List<Item> batchItems = new ArrayList<>();
Item item = new Item();
item.setId("item-test");
item.setCategory("category-1");
item.setScene("scene-1");
item.setStatus(1);
item.setTitle("title-test");
item.setTags("tags-1,tags-2");
item.setPubTime(String.valueOf(System.currentTimeMillis()/1000));
batchItems.add(item);
itemReq.setData(batchItems);
JsonRes<String> jsonRes = recClient.pushItems(itemReq);
```

### recommend
eg:  
```java
RecommendReq recommendReq = new RecommendReq();
recommendReq.setDeviceId("12323-545-14fffe");
recommendReq.setScene("scene-1");
recommendReq.setSize(3);
recommendReq.setUserId("user-9527");
JsonRes<RecommendRes<Item>> jsonRes = recClient.recommend(recommendReq);
```