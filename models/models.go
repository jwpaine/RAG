package models

type EmbedResponse struct {
	Embeddings [][]float64 `json:"embeddings"`
}
