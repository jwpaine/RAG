package database

import (
	"database/sql"
	"errors"
	"fmt"

	_ "modernc.org/sqlite"
)

var (
	SQLiteDriver = "sqlite"
	SQLiteDSN    = "budget.db"
	DB           *sql.DB
)

func Init() (*sql.DB, error) {
	if DB != nil {
		return DB, nil
	}
	var err error
	DB, err = sql.Open(SQLiteDriver, SQLiteDSN) // FIX: assign to package var, not shadow
	if err != nil {
		return nil, fmt.Errorf("failed to connect to SQLite database: %w", err)
	}
	if err = DB.Ping(); err != nil {
		_ = DB.Close()
		DB = nil
		return nil, fmt.Errorf("failed to ping SQLite database: %w", err)
	}
	fmt.Println("Connected to SQLite database")
	return DB, nil
}

func Execute(query string, args ...interface{}) (sql.Result, error) {
	if DB == nil {
		return nil, errors.New("database not initialized; call database.Init() first")
	}
	result, err := DB.Exec(query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to execute query: %w", err)
	}
	return result, nil
}

func Query(query string, args ...interface{}) (*sql.Rows, error) {
	if DB == nil {
		return nil, errors.New("database not initialized; call database.Init() first")
	}
	rows, err := DB.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to execute query: %w", err)
	}
	return rows, nil
}

func Close() error {
	if DB != nil {
		err := DB.Close()
		DB = nil
		return err
	}
	return nil
}
