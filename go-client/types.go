package openrec

// Protocol response codes returned by rec-server.
const (
	CodeSuccess        = 200
	CodeBadRequest     = 400
	CodeNotFound       = 404
	CodeError          = 500
	CodeNotImplemented = 501
	CodeTimeout        = 504
)

// PushCmd is the operation applied to a pushed entity.
type PushCmd string

const (
	PushInsert PushCmd = "INSERT"
	PushUpdate PushCmd = "UPDATE"
	PushDelete PushCmd = "DELETE"
)

const (
	TargetItem = "item"
	TargetUser = "user"
)

// JSONRequest is the request envelope accepted by rec-server.
type JSONRequest[T any] struct {
	RequestID string `json:"requestId"`
	Body      T      `json:"body"`
}

// JSONResponse is the common response envelope returned by rec-server.
// Data is nil when the server returns a JSON null value.
type JSONResponse[T any] struct {
	Code   int    `json:"code"`
	Status bool   `json:"status"`
	Msg    string `json:"msg"`
	Data   *T     `json:"data"`
}

type ItemRequest struct {
	Cmd  PushCmd `json:"cmd"`
	Data []Item  `json:"data,omitempty"`
}

type UserRequest struct {
	Cmd  PushCmd `json:"cmd"`
	Data []User  `json:"data,omitempty"`
}

type EventRequest struct {
	Cmd  PushCmd `json:"cmd"`
	Data []Event `json:"data,omitempty"`
}

type RecommendRequest struct {
	Scene      string         `json:"scene,omitempty"`
	Size       int            `json:"size"`
	UserID     string         `json:"userId,omitempty"`
	DeviceID   string         `json:"deviceId,omitempty"`
	ItemIDs    []string       `json:"itemIds,omitempty"`
	Type       string         `json:"type,omitempty"`
	Debug      bool           `json:"debug"`
	TargetType string         `json:"targetType"`
	Params     map[string]any `json:"params,omitempty"`
}

type RecommendResponse[T any] struct {
	Results     []ScoreResult `json:"results"`
	DetailInfos []T           `json:"detailInfos"`
}

type Item struct {
	ID         string `json:"id,omitempty"`
	Weight     int    `json:"weight"`
	Title      string `json:"title,omitempty"`
	Category   string `json:"category,omitempty"`
	Tags       string `json:"tags,omitempty"`
	Scene      string `json:"scene,omitempty"`
	PubTime    string `json:"pubTime,omitempty"`
	ModifyTime string `json:"modifyTime,omitempty"`
	ExpireTime string `json:"expireTime,omitempty"`
	Status     int    `json:"status"`
	ExtFields  any    `json:"extFields,omitempty"`
}

type User struct {
	ID           string   `json:"id,omitempty"`
	DeviceID     string   `json:"deviceId,omitempty"`
	Name         string   `json:"name,omitempty"`
	Gender       string   `json:"gender,omitempty"`
	Age          int      `json:"age"`
	Country      string   `json:"country,omitempty"`
	City         string   `json:"city,omitempty"`
	Phone        string   `json:"phone,omitempty"`
	Tags         []string `json:"tags,omitempty"`
	RegisterTime string   `json:"registerTime,omitempty"`
	LoginTime    string   `json:"loginTime,omitempty"`
	ExtFields    any      `json:"extFields,omitempty"`
}

type Event struct {
	UserID    string `json:"userId,omitempty"`
	DeviceID  string `json:"deviceId,omitempty"`
	ItemID    string `json:"itemId,omitempty"`
	TraceID   string `json:"traceId,omitempty"`
	Scene     string `json:"scene,omitempty"`
	Type      string `json:"type,omitempty"`
	Value     string `json:"value,omitempty"`
	Time      string `json:"time,omitempty"`
	IsLogin   bool   `json:"isLogin"`
	ExtFields any    `json:"extFields,omitempty"`
}

type ScoreResult struct {
	ID                string             `json:"id,omitempty"`
	Score             float64            `json:"score"`
	RecallFrom        string             `json:"recallFrom,omitempty"`
	RecallScore       *float64           `json:"recallScore,omitempty"`
	RecallFusionScore *float64           `json:"recallFusionScore,omitempty"`
	RankScore         *float64           `json:"rankScore,omitempty"`
	RecallScores      map[string]float64 `json:"recallScores,omitempty"`
}

type DislikeValue struct {
	ID       string   `json:"id,omitempty"`
	Category string   `json:"category,omitempty"`
	Tags     []string `json:"tags"`
}

type VectorResult struct {
	ID     string    `json:"id,omitempty"`
	Vector []float64 `json:"vector,omitempty"`
}
