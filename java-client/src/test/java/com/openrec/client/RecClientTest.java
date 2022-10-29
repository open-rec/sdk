package com.openrec.client;

import com.openrec.proto.JsonRes;
import com.openrec.proto.biz.push.EventReq;
import com.openrec.proto.biz.push.ItemReq;
import com.openrec.proto.biz.push.PushCmd;
import com.openrec.proto.biz.push.UserReq;
import com.openrec.proto.biz.recommend.RecommendReq;
import com.openrec.proto.biz.recommend.RecommendRes;
import com.openrec.proto.model.Event;
import com.openrec.proto.model.Item;
import com.openrec.proto.model.User;
import org.junit.Assert;

import java.util.ArrayList;
import java.util.List;

public class RecClientTest {

    private static final String TEST_ENDPOINT = "http://localhost:13579";
    private RecClient recClient;

    @org.junit.Before
    public void setUp() throws Exception {
        recClient = new RecClient(TEST_ENDPOINT);
    }

    @org.junit.Test
    public void pushDocs() {
        ItemReq itemReq = new ItemReq();
        itemReq.setCmd(PushCmd.INSERT);
        List<Item> batchItems = new ArrayList<>();
        Item item = new Item();
        item.setId("item-1");
        item.setCategory("category-1");
        item.setScene("scene-1");
        item.setStatus(1);
        item.setTitle("title-test");
        item.setTags("tags-1,tags-2");
        item.setPubTime("2022-01-01");
        batchItems.add(item);
        JsonRes<String> jsonRes = recClient.pushItems(itemReq);
        Assert.assertTrue(jsonRes.isStatus());
        Assert.assertEquals(jsonRes.getCode(), 200);

        UserReq userReq = new UserReq();
        userReq.setCmd(PushCmd.INSERT);
        List<User> batchUsers = new ArrayList<>();
        User user = new User();
        user.setId("user-1");
        user.setAge(30);
        user.setDeviceId("bh-89757");
        user.setCity("hangzhou");
        user.setCountry("China");
        user.setGender("male");
        batchUsers.add(user);
        jsonRes = recClient.pushUsers(userReq);
        Assert.assertTrue(jsonRes.isStatus());
        Assert.assertEquals(jsonRes.getCode(), 200);

        EventReq eventReq = new EventReq();
        eventReq.setCmd(PushCmd.INSERT);
        List<Event> batchEvents = new ArrayList<>();
        Event event = new Event();
        event.setItemId("item-1");
        event.setUserId("user-1");
        event.setLogin(true);
        event.setDeviceId("bh-89757");
        event.setType("click");
        event.setTraceId("open-rec");
        event.setTime("2022-01-01");
        batchEvents.add(event);
        jsonRes = recClient.pushEvents(eventReq);
        Assert.assertTrue(jsonRes.isStatus());
        Assert.assertEquals(jsonRes.getCode(), 200);
    }

    @org.junit.Test
    public void recommend() {
        RecommendReq recommendReq = new RecommendReq();
        recommendReq.setDeviceId("12323-545-14fffe");
        recommendReq.setSceneId("scene-1");
        recommendReq.setSize(3);
        recommendReq.setType("gul");
        recommendReq.setUserId("user-9527");
        JsonRes<RecommendRes<Item>> jsonRes = recClient.recommend(recommendReq);
        Assert.assertTrue(jsonRes.isStatus());
        Assert.assertEquals(jsonRes.getCode(), 200);
        Assert.assertNotNull(jsonRes.getData());
    }
}