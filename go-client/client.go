package openrec

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
)

const (
	recommendPath     = "/api/recommend"
	recommendItemPath = "/api/recommend/item"
	recommendUserPath = "/api/recommend/user"
	pushItemPath      = "/api/push/item"
	pushUserPath      = "/api/push/user"
	pushEventPath     = "/api/push/event"
)

// Client is safe for concurrent use when its HTTP client is safe for concurrent use.
type Client struct {
	endpoint   string
	httpClient *http.Client
}

func NewClient(endpoint string) *Client {
	return NewClientWithHTTPClient(endpoint, http.DefaultClient)
}

func NewClientWithHTTPClient(endpoint string, httpClient *http.Client) *Client {
	if httpClient == nil {
		httpClient = http.DefaultClient
	}
	return &Client{endpoint: strings.TrimRight(endpoint, "/"), httpClient: httpClient}
}

func NewJSONRequest[T any](body T) JSONRequest[T] {
	return JSONRequest[T]{RequestID: newRequestID(), Body: body}
}

func (c *Client) PushItems(ctx context.Context, request ItemRequest) (*JSONResponse[string], error) {
	return c.PushItemsWithRequest(ctx, NewJSONRequest(request))
}

func (c *Client) PushUsers(ctx context.Context, request UserRequest) (*JSONResponse[string], error) {
	return c.PushUsersWithRequest(ctx, NewJSONRequest(request))
}

func (c *Client) PushEvents(ctx context.Context, request EventRequest) (*JSONResponse[string], error) {
	return c.PushEventsWithRequest(ctx, NewJSONRequest(request))
}

func (c *Client) PushItemsWithRequest(ctx context.Context, request JSONRequest[ItemRequest]) (*JSONResponse[string], error) {
	request.Body.Cmd = defaultPushCmd(request.Body.Cmd)
	return post[string](ctx, c, pushItemPath, request)
}

func (c *Client) PushUsersWithRequest(ctx context.Context, request JSONRequest[UserRequest]) (*JSONResponse[string], error) {
	request.Body.Cmd = defaultPushCmd(request.Body.Cmd)
	return post[string](ctx, c, pushUserPath, request)
}

func (c *Client) PushEventsWithRequest(ctx context.Context, request JSONRequest[EventRequest]) (*JSONResponse[string], error) {
	request.Body.Cmd = defaultPushCmd(request.Body.Cmd)
	return post[string](ctx, c, pushEventPath, request)
}

// Recommend calls the legacy item-recommendation endpoint.
func (c *Client) Recommend(ctx context.Context, request RecommendRequest) (*JSONResponse[RecommendResponse[Item]], error) {
	return c.RecommendWithRequest(ctx, NewJSONRequest(request))
}

func (c *Client) RecommendItems(ctx context.Context, request RecommendRequest) (*JSONResponse[RecommendResponse[Item]], error) {
	return c.RecommendItemsWithRequest(ctx, NewJSONRequest(request))
}

func (c *Client) RecommendUsers(ctx context.Context, request RecommendRequest) (*JSONResponse[RecommendResponse[User]], error) {
	return c.RecommendUsersWithRequest(ctx, NewJSONRequest(request))
}

func (c *Client) RecommendWithRequest(ctx context.Context, request JSONRequest[RecommendRequest]) (*JSONResponse[RecommendResponse[Item]], error) {
	defaultRecommendTarget(&request.Body)
	return post[RecommendResponse[Item]](ctx, c, recommendPath, request)
}

func (c *Client) RecommendItemsWithRequest(ctx context.Context, request JSONRequest[RecommendRequest]) (*JSONResponse[RecommendResponse[Item]], error) {
	defaultRecommendTarget(&request.Body)
	return post[RecommendResponse[Item]](ctx, c, recommendItemPath, request)
}

func (c *Client) RecommendUsersWithRequest(ctx context.Context, request JSONRequest[RecommendRequest]) (*JSONResponse[RecommendResponse[User]], error) {
	defaultRecommendTarget(&request.Body)
	return post[RecommendResponse[User]](ctx, c, recommendUserPath, request)
}

func post[T any](ctx context.Context, client *Client, path string, payload any) (*JSONResponse[T], error) {
	if client == nil || client.httpClient == nil {
		return nil, errors.New("openrec: nil client")
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("openrec: encode request: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, client.endpoint+path, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("openrec: create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json; charset=utf-8")

	response, err := client.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("openrec: send request: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < http.StatusOK || response.StatusCode >= http.StatusMultipleChoices {
		_, _ = io.Copy(io.Discard, response.Body)
		return nil, nil
	}

	var result JSONResponse[T]
	if err := json.NewDecoder(response.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("openrec: decode response: %w", err)
	}
	return &result, nil
}

func defaultPushCmd(cmd PushCmd) PushCmd {
	if cmd == "" {
		return PushInsert
	}
	return cmd
}

func defaultRecommendTarget(request *RecommendRequest) {
	if request.TargetType == "" {
		request.TargetType = TargetItem
	}
}

func newRequestID() string {
	var value [16]byte
	if _, err := rand.Read(value[:]); err != nil {
		panic(fmt.Sprintf("openrec: generate request ID: %v", err))
	}
	value[6] = (value[6] & 0x0f) | 0x40
	value[8] = (value[8] & 0x3f) | 0x80
	var out [36]byte
	hex.Encode(out[0:8], value[0:4])
	out[8] = '-'
	hex.Encode(out[9:13], value[4:6])
	out[13] = '-'
	hex.Encode(out[14:18], value[6:8])
	out[18] = '-'
	hex.Encode(out[19:23], value[8:10])
	out[23] = '-'
	hex.Encode(out[24:36], value[10:16])
	return string(out[:])
}
