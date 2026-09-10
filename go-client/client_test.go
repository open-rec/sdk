package openrec

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestClientPathsAndPayloads(t *testing.T) {
	var paths []string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		paths = append(paths, r.URL.Path)
		if got := r.Header.Get("Content-Type"); got != "application/json; charset=utf-8" {
			t.Errorf("Content-Type = %q", got)
		}
		var envelope struct {
			RequestID string          `json:"requestId"`
			Body      json.RawMessage `json:"body"`
		}
		if err := json.NewDecoder(r.Body).Decode(&envelope); err != nil {
			t.Fatal(err)
		}
		if envelope.RequestID == "" {
			t.Error("requestId is empty")
		}
		if strings.HasPrefix(r.URL.Path, "/api/recommend") {
			_, _ = io.WriteString(w, `{"code":200,"status":true,"msg":"","data":{"results":[{"id":"1","score":1.5}],"detailInfos":[{"id":"1"}]}}`)
			return
		}
		var push struct {
			Cmd PushCmd `json:"cmd"`
		}
		if err := json.Unmarshal(envelope.Body, &push); err != nil {
			t.Fatal(err)
		}
		if push.Cmd != PushInsert {
			t.Errorf("default cmd = %q", push.Cmd)
		}
		_, _ = io.WriteString(w, `{"code":200,"status":true,"msg":"","data":"ok"}`)
	}))
	defer server.Close()

	client := NewClient(server.URL + "/")
	ctx := context.Background()
	if _, err := client.PushItems(ctx, ItemRequest{Data: []Item{{ID: "i1"}}}); err != nil {
		t.Fatal(err)
	}
	if _, err := client.PushUsers(ctx, UserRequest{Data: []User{{ID: "u1"}}}); err != nil {
		t.Fatal(err)
	}
	if _, err := client.PushEvents(ctx, EventRequest{Data: []Event{{UserID: "u1", ItemID: "i1"}}}); err != nil {
		t.Fatal(err)
	}
	legacy, err := client.Recommend(ctx, RecommendRequest{Scene: "s", Size: 3})
	if err != nil {
		t.Fatal(err)
	}
	if legacy.Data == nil || len(legacy.Data.Results) != 1 {
		t.Fatalf("legacy response = %#v", legacy)
	}
	items, err := client.RecommendItems(ctx, RecommendRequest{Scene: "s", Debug: true})
	if err != nil {
		t.Fatal(err)
	}
	if items.Data == nil || len(items.Data.DetailInfos) != 1 {
		t.Fatalf("item response = %#v", items)
	}
	users, err := client.RecommendUsers(ctx, RecommendRequest{Scene: "s"})
	if err != nil {
		t.Fatal(err)
	}
	if users.Data == nil || len(users.Data.DetailInfos) != 1 {
		t.Fatalf("user response = %#v", users)
	}

	want := []string{"/api/push/item", "/api/push/user", "/api/push/event", "/api/recommend", "/api/recommend/item", "/api/recommend/user"}
	if strings.Join(paths, ",") != strings.Join(want, ",") {
		t.Fatalf("paths = %v, want %v", paths, want)
	}
}

func TestExplicitRequestID(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var request JSONRequest[RecommendRequest]
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			t.Fatal(err)
		}
		if request.RequestID != "trace-42" {
			t.Errorf("requestId = %q", request.RequestID)
		}
		if request.Body.TargetType != TargetItem {
			t.Errorf("targetType = %q", request.Body.TargetType)
		}
		_, _ = io.WriteString(w, `{"code":200,"status":true,"msg":"","data":{"results":[],"detailInfos":null}}`)
	}))
	defer server.Close()

	request := JSONRequest[RecommendRequest]{RequestID: "trace-42", Body: RecommendRequest{}}
	if _, err := NewClient(server.URL).RecommendItemsWithRequest(context.Background(), request); err != nil {
		t.Fatal(err)
	}
}

func TestNon2xxReturnsNil(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { http.Error(w, "no", http.StatusBadRequest) }))
	defer server.Close()
	response, err := NewClient(server.URL).PushItems(context.Background(), ItemRequest{})
	if err != nil || response != nil {
		t.Fatalf("response = %#v, error = %v", response, err)
	}
}

func TestDecodeAndTransportErrors(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { _, _ = io.WriteString(w, "not-json") }))
	defer server.Close()
	if _, err := NewClient(server.URL).PushItems(context.Background(), ItemRequest{}); err == nil || !strings.Contains(err.Error(), "decode response") {
		t.Fatalf("error = %v", err)
	}

	client := NewClientWithHTTPClient("http://openrec.test", &http.Client{Transport: roundTripFunc(func(*http.Request) (*http.Response, error) {
		return nil, errors.New("offline")
	})})
	if _, err := client.PushItems(context.Background(), ItemRequest{}); err == nil || !strings.Contains(err.Error(), "send request") {
		t.Fatalf("error = %v", err)
	}
}

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(request *http.Request) (*http.Response, error) { return f(request) }
