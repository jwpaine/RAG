package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"gobudget/database"
	Models "gobudget/models"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

func main() {

	db, err := database.GetDatabase("pg")
	if err != nil {
		log.Fatal(err)
	}

	config := map[string]string{
		"host":     "localhost",
		"port":     "5432",
		"user":     "postgres",
		"password": "postgres",
		"dbname":   "vectordb",
	}

	if err := db.Connect(config); err != nil {
		log.Fatal(err)
	}

	// initalize
	fmt.Println("Initializing database...")
	if err := db.Init(); err != nil {
		log.Fatal(err)
	}

	// example text chunk
	text := "I am afraid"
	embedding, err := getEmbedding(text)
	if err != nil {
		log.Fatal(err)
	}

	// retrieving similar embeddings
	similar, err := db.GetSimilarities(embedding, 5)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Similar: %v\n", similar)

	defer db.Close()
}

func loadQuotes(db database.Database) error {
	file := "yoda_quotes.csv"
	f, err := os.Open(file)
	if err != nil {
		return fmt.Errorf("failed to open %s: %w", file, err)
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	i := 0
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		i++
		fmt.Printf("Processing record %d: %s\n", i, line)
		embedding, err := getEmbedding(line)
		if err != nil {
			return fmt.Errorf("getting embedding: %w", err)
		}
		title := fmt.Sprintf("Yoda Quote %d", i)
		metadata := "{}" // empty JSON object
		err = db.InsertEmbedding(line, embedding, title, metadata)
		if err != nil {
			return fmt.Errorf("inserting embedding: %w", err)
		}
		fmt.Printf("Inserted record %d successfully.\n", i)
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("reading file: %w", err)
	}
	return nil
}

func getEmbedding(text string) ([]float64, error) {
	// the embedding server endpoint

	apiURL := "http://localhost:8000/embed"

	// prepare the payload (Python expects a list of strings)
	payload, err := json.Marshal([]string{text})
	if err != nil {
		panic(err)
	}

	fmt.Printf("Requesting embedding for text: %s\n", text)

	client := &http.Client{Timeout: 20 * time.Second}
	resp, err := client.Post(apiURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		panic(fmt.Errorf("failed to call embedding API: %w", err))
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		panic(fmt.Errorf("embedding API returned status: %s", resp.Status))
	}

	var result Models.EmbedResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		panic(fmt.Errorf("failed to decode response: %w", err))
	}

	// show summary
	fmt.Printf("Embedding vector length: %d\n", len(result.Embeddings[0]))
	fmt.Printf("First 8 dimensions: %.4f\n", result.Embeddings[0][:8])

	return result.Embeddings[0], nil

}
