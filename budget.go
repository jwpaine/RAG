package main

import (
	"fmt"
	Database "gobudget/database"
	Account "gobudget/models"
)

func main() {
	fmt.Println("Budget management application")

	db, err := Database.Init()
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create budgets table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS accounts (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		type TEXT NOT NULL,
		balance REAL NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	// add account
	err = Account.Add("Checking Account", "Checking", 1000.00)
	if err != nil {
		panic(err)
	}

	// retrieve accounts
	accounts, err := Account.GetAll()
	if err != nil {
		panic(err)
	}

	for _, acc := range accounts {
		fmt.Printf("Account ID: %d, Name: %s, Type: %s, Balance: %.2f\n", acc.ID, acc.Name, acc.Type, acc.Balance)
	}

	// delete account
	if len(accounts) > 0 {
		err = Account.Delete(accounts[0].ID)
		if err != nil {
			panic(err)
		}
		fmt.Printf("Deleted account with ID: %d\n", accounts[0].ID)
	}

}
