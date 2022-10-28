package com.openrec.client.utils;

import com.google.gson.Gson;

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
}
