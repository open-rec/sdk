package com.openrec.client;

/** HTTP transport failure. Business errors still use the existing JsonRes contract. */
public class RecClientHttpException extends RuntimeException {
    private final int statusCode;
    private final String responseBody;

    public RecClientHttpException(int statusCode, String responseBody) {
        super("OpenRec HTTP " + statusCode + ": " + responseBody);
        this.statusCode = statusCode;
        this.responseBody = responseBody;
    }

    public int getStatusCode() {
        return statusCode;
    }

    public String getResponseBody() {
        return responseBody;
    }
}
