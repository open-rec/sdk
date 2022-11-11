package com.openrec.client.utils;

import com.google.gson.Gson;
import com.google.gson.internal.$Gson$Preconditions;
import com.google.gson.internal.$Gson$Types;
import com.openrec.proto.JsonResType;

import java.lang.reflect.Type;

public class ToolUtils {

    private static Gson gson;

    static {
        gson = new Gson();
    }

    public static String objToJson(Object obj) {
        return gson.toJson(obj);
    }

    public static <T> T jsonToObj(String json, Class<T> clazz) {
        return gson.fromJson(json, clazz);
    }

    public static <T> T jsonToObj(String json, Type type) {
        return gson.fromJson(json, type);
    }

    public static <T> T jsonToResponse(String json, Class clazz) {
        return jsonToObj(json, $Gson$Types.canonicalize($Gson$Preconditions.checkNotNull(new JsonResType(clazz))));
    }

    public static <T> T jsonToResponse(String json, Type type) {
        return jsonToObj(json, $Gson$Types.canonicalize($Gson$Preconditions.checkNotNull(type)));
    }
}
