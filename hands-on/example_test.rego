package petstore.authz

test_allow_positive {
    allow with input as {
        "subject": {
            "user": "bob",
        },
        "method": "GET",
        "path": ["accounts", "bob"],
    }

    allow with input as {
        "subject": {
            "groups": ["customer-service"],
            "user": "alice",
        },
        "method": "GET",
        "path": ["accounts", "bob"],
    } with data.petstore.tickets as {
        "bob": [
            {"assignee": "alice"},
        ],
    }
}

test_allow_negative {
    not allow with input as {
        "subject": {
            "user": "bob",
        },
        "method": "GET",
        "path": ["accounts", "alice"],
    }

    not allow with input as {
        "subject": {
            "groups": ["customer-service"],
            "user": "alice",
        },
        "method": "GET",
        "path": ["accounts", "bob"],
    } with data.petstore.tickets as {
        "bob": [
            {"assignee": "karen"},
        ],
    }
}
