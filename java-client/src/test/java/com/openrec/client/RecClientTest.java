package com.openrec.client;

import com.openrec.proto.JsonRes;
import com.openrec.proto.biz.recommend.RecommendReq;
import com.openrec.proto.biz.recommend.RecommendRes;
import com.openrec.proto.model.Item;
import org.junit.Assert;

public class RecClientTest {

    private static final String TEST_ENDPOINT = "http://localhost:13579";
    private RecClient recClient;

    @org.junit.Before
    public void setUp() throws Exception {
        recClient = new RecClient(TEST_ENDPOINT);
    }

    @org.junit.Test
    public void pushItems() {
    }

    @org.junit.Test
    public void pushUsers() {
    }

    @org.junit.Test
    public void pushEvents() {
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