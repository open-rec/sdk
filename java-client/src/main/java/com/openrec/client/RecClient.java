package com.openrec.client;

import com.google.gson.reflect.TypeToken;
import com.openrec.client.utils.ToolUtils;
import com.openrec.proto.JsonReq;
import com.openrec.proto.JsonRes;
import com.openrec.proto.biz.push.EventReq;
import com.openrec.proto.biz.push.ItemReq;
import com.openrec.proto.biz.push.UserReq;
import com.openrec.proto.biz.recommend.RecommendReq;
import com.openrec.proto.biz.recommend.RecommendRes;
import com.openrec.proto.model.Item;
import okhttp3.*;

import java.io.IOException;

public class RecClient {

    private static final MediaType PROTOCOL_TYPE = MediaType.
            parse("application/json; charset=utf-8");
    private static final String API_PATH = "/api";
    private static final String RECOMMEND_PATH = API_PATH + "/recommend";
    private static final String PUSH_PATH = API_PATH + "/push";
    private static final String PUSH_ITEM_PATH = PUSH_PATH + "/item";
    private static final String PUSH_USER_PATH = PUSH_PATH + "/user";
    private static final String PUSH_EVENT_PATH = PUSH_PATH + "/event";

    private String endpoint;
    private OkHttpClient client;

    public RecClient(String endpoint) {
        this.endpoint = endpoint;
        this.client = new OkHttpClient();
    }

    private <RES> JsonRes<RES> post(String path, Object data, Class clazz) {
        RequestBody requestBody = RequestBody.create(PROTOCOL_TYPE, ToolUtils.objToJson(data));
        Request request = new Request.Builder()
                .url(endpoint + path)
                .post(requestBody)
                .build();
        JsonRes<RES> jsonRes = null;
        try {
            Response strRes = client.newCall(request).execute();
            if(strRes!=null && strRes.isSuccessful()) {
                jsonRes = ToolUtils.jsonToResponse(strRes.body().string(), clazz);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return jsonRes;
    }

    public JsonRes<String> pushItems(ItemReq itemReq) {
        return pushItems(new JsonReq<>(itemReq));
    }

    public JsonRes<String> pushUsers(UserReq userReq) {
        return pushUsers(new JsonReq<>(userReq));
    }

    public JsonRes<String> pushEvents(EventReq eventReq) {
        return pushEvents(new JsonReq<>(eventReq));
    }

    public JsonRes<RecommendRes<Item>> recommend(RecommendReq recReq) {
        return recommend(new JsonReq<>(recReq));
    }

    public JsonRes<String> pushItems(JsonReq<ItemReq> itemReq) {
        return post(PUSH_ITEM_PATH, itemReq, String.class);
    }

    public JsonRes<String> pushUsers(JsonReq<UserReq> userReq) {
        return post(PUSH_USER_PATH, userReq, String.class);
    }

    public JsonRes<String> pushEvents(JsonReq<EventReq> eventReq) {
        return post(PUSH_EVENT_PATH, eventReq, String.class);
    }

    public JsonRes<RecommendRes<Item>> recommend(JsonReq<RecommendReq> recReq) {
        return post(RECOMMEND_PATH, recReq, RecommendRes.class);
    }
}
