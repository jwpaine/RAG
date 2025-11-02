package database

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

type PGDatabase struct {
	db *sql.DB
}

func (pg *PGDatabase) Connect(config map[string]string) error {
	psqlInfo := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		config["host"], config["port"], config["user"], config["password"], config["dbname"],
	)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return fmt.Errorf("failed to connect to PostgreSQL: %w", err)
	}

	if err = db.Ping(); err != nil {
		db.Close()
		return fmt.Errorf("failed to ping PostgreSQL: %w", err)
	}

	pg.db = db
	fmt.Println("Connected to PostgreSQL database")
	return nil
}

func (pg *PGDatabase) Close() error {
	if pg.db != nil {
		return pg.db.Close()
	}
	return nil
}

func (pg *PGDatabase) Init() error {
	_, err := pg.db.Exec(`
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        embedding VECTOR(384), -- all-MiniLM-L6-v2 embedding size
        title TEXT,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP DEFAULT NOW()
    );
`)
	if err != nil {
		return err
	}
	return nil
}

func (pg *PGDatabase) GetSimilarities(embedding []float64, limit int) ([]string, error) {
	vectorStr := toPGVector(embedding)

	// Use parameterized query instead of fmt.Sprintf for safety
	query := `
		SELECT content
		FROM documents
		ORDER BY embedding <-> $1
		LIMIT $2;
	`

	rows, err := pg.db.Query(query, vectorStr, limit)
	if err != nil {
		return nil, fmt.Errorf("querying similarities: %w", err)
	}
	defer rows.Close()

	var content []string
	for rows.Next() {
		var c string
		if err := rows.Scan(&c); err != nil {
			return nil, fmt.Errorf("scanning row: %w", err)
		}
		content = append(content, c)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("row iteration: %w", err)
	}

	return content, nil
}

func (pg *PGDatabase) ExecQuery(query string, args ...interface{}) error {
	_, err := pg.db.Exec(query, args...)
	return err
}

func (pg *PGDatabase) InsertEmbedding(content string, embedding []float64, title string, metadata string) error {
	// Convert []float64 → Postgres vector literal
	vectorStr := toPGVector(embedding)

	query := `INSERT INTO documents (content, embedding, title, metadata)
	          VALUES ($1, $2, $3, $4)`
	err := pg.ExecQuery(query, content, vectorStr, title, metadata)
	return err
}

// helper to format vector
func toPGVector(vec []float64) string {
	s := "["
	for i, v := range vec {
		if i > 0 {
			s += ", "
		}
		s += fmt.Sprintf("%f", v)
	}
	s += "]"
	return s
}
