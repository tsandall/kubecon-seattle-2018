package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"path"

	"github.com/open-policy-agent/opa/loader"
	"github.com/open-policy-agent/opa/rego"
)

func main() {

	if len(os.Args) != 2 {
		log.Fatalf("Usage: %v <bundle.tar.gz>", path.Base((os.Args[0])))
	}

	bundle, err := loader.All([]string{os.Args[1]})
	if err != nil {
		log.Fatalf("Failed to load bundle from disk: %v", err)
	}

	compiler, err := bundle.Compiler()
	if err != nil {
		log.Fatalf("Failed to compile policies in bundle: %v", err)
	}

	store, err := bundle.Store()
	if err != nil {
		log.Fatalf("Failed to create storage from bundle: %v", err)
	}

	var input interface{}

	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		log.Fatalf("Failed to decode input: %v", err)
	}

	r := rego.New(
		rego.Compiler(compiler),
		rego.Store(store),
		rego.Input(input),
		rego.Query("data.petstore.authz.allow = allowed"),
	)

	rs, err := r.Eval(context.Background())
	if err != nil {
		log.Fatalf("Failed to evaluate policy: %v", err)
	}

	if len(rs) == 0 {
		log.Fatal("Policy decision is undefined. Policy query returned no results.")
	}

	allowed, ok := rs[0].Bindings["allowed"].(bool)

	if !ok || !allowed {
		log.Println("Policy decision: DENY")
	} else {
		log.Println("Policy decision: ALLOW")
	}
}
