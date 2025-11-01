package models

import (
	"fmt"
	Database "gobudget/database"
)

func Add(name, accType string, balance float64) error {
	insertSQL := `INSERT INTO accounts (name, type, balance) VALUES (?, ?, ?)`
	_, err := Database.Execute(insertSQL, name, accType, balance)
	return err
}

func Delete(id int) error {
	deleteSQL := `DELETE FROM accounts WHERE id = ?`
	_, err := Database.Execute(deleteSQL, id)
	return err
}

func GetAll() ([]Account, error) {
	rows, err := Database.Query("SELECT id, name, type, balance FROM accounts")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var accounts []Account
	for rows.Next() {
		var acc Account
		err := rows.Scan(&acc.ID, &acc.Name, &acc.Type, &acc.Balance)
		if err != nil {
			return nil, fmt.Errorf("failed to scan account: %v", err)
		}
		accounts = append(accounts, acc)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return accounts, nil
}
