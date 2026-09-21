package com.openrec.client;

import com.openrec.proto.biz.push.ItemReq;
import com.openrec.proto.biz.recommend.RecommendReq;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Protocol;
import okhttp3.Response;
import okhttp3.ResponseBody;
import okio.Buffer;
import okio.BufferedSource;
import okio.ForwardingSource;
import okio.Okio;
import org.junit.Test;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicBoolean;

import static org.junit.Assert.*;

public class RecClientTransportTest {
    @Test
    public void failedPushClosesBodyAndPreservesStatusWithBoundedDetail() {
        AtomicBoolean closed = new AtomicBoolean();
        RecClient client = client(503, new String(new char[4096]).replace('\0', 'x'), closed);
        try {
            client.pushItems(new ItemReq());
            fail("HTTP error must not return null");
        } catch (RecClientHttpException error) {
            assertEquals(503, error.getStatusCode());
            assertEquals(1024, error.getResponseBody().length());
        }
        assertTrue(closed.get());
    }

    @Test
    public void failedRecommendationClosesBody() {
        AtomicBoolean closed = new AtomicBoolean();
        try {
            client(429, "busy", closed).recommendItems(new RecommendReq());
            fail("HTTP error must not return null");
        } catch (RecClientHttpException error) {
            assertEquals(429, error.getStatusCode());
            assertEquals("busy", error.getResponseBody());
        }
        assertTrue(closed.get());
    }

    @Test
    public void malformedSuccessfulResponseStillClosesBody() {
        AtomicBoolean closed = new AtomicBoolean();
        try {
            client(200, "{", closed).pushItems(new ItemReq());
            fail("invalid JSON must fail");
        } catch (RuntimeException expected) {
            assertTrue(closed.get());
        }
    }

    @Test
    public void nullSuccessfulResponseFailsAndClosesBody() {
        AtomicBoolean closed = new AtomicBoolean();
        try {
            client(200, "null", closed).pushItems(new ItemReq());
            fail("null JSON must fail");
        } catch (RuntimeException expected) {
            assertTrue(closed.get());
        }
    }

    private RecClient client(int status, String text, AtomicBoolean closed) {
        BufferedSource source = Okio.buffer(new ForwardingSource(new Buffer().writeUtf8(text)) {
            @Override
            public void close() throws IOException {
                closed.set(true);
                super.close();
            }
        });
        ResponseBody body = new ResponseBody() {
            @Override
            public MediaType contentType() {
                return MediaType.parse("application/json");
            }
            @Override
            public long contentLength() {
                return text.length();
            }
            @Override
            public BufferedSource source() {
                return source;
            }
        };
        OkHttpClient http = new OkHttpClient.Builder().addInterceptor(chain -> new Response.Builder()
                .request(chain.request()).protocol(Protocol.HTTP_1_1).code(status)
                .message("test").body(body).build()).build();
        return new RecClient("http://openrec.test", http);
    }
}
