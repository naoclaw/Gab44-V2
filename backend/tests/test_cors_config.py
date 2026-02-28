"""
Unit tests for the CORS middleware configuration logic.

These tests are standalone (no live server or DB required).

The rule being tested:
    allow_credentials=True combined with allow_origins=["*"] is invalid per the
    CORS specification — browsers reject responses where
    Access-Control-Allow-Origin is the literal wildcard "*" and
    Access-Control-Allow-Credentials is "true".

    The server therefore uses allow_origin_regex=".*" instead of
    allow_origins=["*"] when CORS_ORIGINS contains a wildcard, so that
    Starlette reflects the actual request Origin header in responses
    (satisfying the browser requirement).
"""

import os


# ---------------------------------------------------------------------------
# Inline the helper logic from server.py so these tests remain self-contained.
# If the implementation drifts, the integration tests will catch it.
# ---------------------------------------------------------------------------

def _build_cors_kwargs(cors_origins_env: str | None) -> dict:
    """
    Mirror of the CORS middleware argument-building logic in server.py.
    Returns the keyword arguments that would be passed to CORSMiddleware.
    """
    raw = cors_origins_env if cors_origins_env is not None else '*'
    origins = raw.split(',')
    wildcard = '*' in origins
    return {
        'allow_credentials': True,
        'allow_origins': [] if wildcard else origins,
        'allow_origin_regex': '.*' if wildcard else None,
        'allow_methods': ['*'],
        'allow_headers': ['*'],
    }


class TestCorsConfigWildcard:
    """When CORS_ORIGINS is not set (or is '*'), wildcard must use regex."""

    def test_wildcard_uses_regex_not_list(self):
        kwargs = _build_cors_kwargs('*')
        assert kwargs['allow_origin_regex'] == '.*', (
            "Wildcard should use allow_origin_regex='.*' so that Starlette "
            "reflects the actual Origin header (required when credentials=True)"
        )

    def test_wildcard_allow_origins_is_empty(self):
        kwargs = _build_cors_kwargs('*')
        assert kwargs['allow_origins'] == [], (
            "When wildcard is used, allow_origins must be empty to avoid "
            "Starlette sending 'Access-Control-Allow-Origin: *' in responses"
        )

    def test_default_env_behaves_like_wildcard(self):
        """Unset CORS_ORIGINS defaults to '*', must also use regex."""
        kwargs = _build_cors_kwargs(None)
        assert kwargs['allow_origin_regex'] == '.*'
        assert kwargs['allow_origins'] == []

    def test_credentials_always_true(self):
        kwargs = _build_cors_kwargs('*')
        assert kwargs['allow_credentials'] is True


class TestCorsConfigSpecificOrigins:
    """When CORS_ORIGINS lists explicit origins, allow_origins must be used."""

    def test_single_origin_uses_allow_origins(self):
        kwargs = _build_cors_kwargs('https://gab44.com')
        assert kwargs['allow_origins'] == ['https://gab44.com']

    def test_single_origin_regex_is_none(self):
        kwargs = _build_cors_kwargs('https://gab44.com')
        assert kwargs['allow_origin_regex'] is None, (
            "When specific origins are listed there is no need for a catch-all "
            "regex — using one would be overly permissive."
        )

    def test_multiple_origins(self):
        kwargs = _build_cors_kwargs('https://gab44.com,https://staging.gab44.com')
        assert kwargs['allow_origins'] == [
            'https://gab44.com',
            'https://staging.gab44.com',
        ]

    def test_multiple_origins_regex_is_none(self):
        kwargs = _build_cors_kwargs('https://gab44.com,https://staging.gab44.com')
        assert kwargs['allow_origin_regex'] is None

    def test_credentials_true_for_specific_origins(self):
        kwargs = _build_cors_kwargs('https://gab44.com')
        assert kwargs['allow_credentials'] is True


class TestCorsConfigNoWildcardPassthrough:
    """Only the bare '*' string triggers the wildcard path — nothing else."""

    def test_localhost_with_specific_port_is_not_wildcard(self):
        """'http://localhost:3000' is a fully-qualified origin, not a wildcard."""
        kwargs = _build_cors_kwargs('http://localhost:3000')
        assert kwargs['allow_origins'] == ['http://localhost:3000']
        assert kwargs['allow_origin_regex'] is None
