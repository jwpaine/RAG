package database

type Database interface {
	Connect(config map[string]string) error
	Init() error
	GetSimilarities(embedding []float64, limit int) ([]string, error)
	ExecQuery(query string, args ...interface{}) error
	InsertEmbedding(content string, embedding []float64, title string, metadata string) error
	Close() error
}

func GetDatabase(driver string) (Database, error) {
	// only pg for now
	return &PGDatabase{}, nil
}
