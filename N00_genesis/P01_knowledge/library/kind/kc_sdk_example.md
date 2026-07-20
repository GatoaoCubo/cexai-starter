---
id: kc_sdk_example
kind: knowledge_card
8f: F3_inject
title: SDK Example Integration Patterns
version: 1.0.0
quality: null
pillar: P01
tldr: "Multi-language SDK code samples showing canonical integration patterns for API authentication and usage"
when_to_use: "When providing developers with copy-paste SDK examples in Python, JavaScript, or Java"
keywords: [api key authentication, asynchronous pattern, non-blocking i/o, type-safe method signatures, environment variable support]
density_score: 1.0
related:
  - bld_output_template_sdk_example
  - bld_config_sdk_example
  - bld_collaboration_sdk_example
  - p01_kc_competitor_openai_sdk
  - sdk-example-builder
---

# SDK Integration Patterns

This card shows copy-paste client setup across Python, JavaScript, and Java, plus the shared conventions every language binding follows.

## Python
```python
from cex_sdk import SDK

sdk = SDK(api_key="your_key")
response = sdk.create_project(name="Example Project")
print(response.status_code)
```

## JavaScript
```javascript
const SDK = require('cex-sdk');
const sdk = new SDK({ apiKey: 'your_key' });
sdk.createProject("Example Project")
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

## Java
```java
import com.cex.sdk.SDK;

public class Example {
    public static void main(String[] args) {
        SDK sdk = new SDK("your_key");
        System.out.println(sdk.createProject("Example Project"));
    }
}
```

## Key Patterns
1. API key authentication via constructor
2. Asynchronous pattern for non-blocking I/O
3. Consistent error handling patterns
4. Type-safe method signatures
5. Environment variable support for credentials

## How to use

```text
ROLE: you are producing copy-paste SDK examples for a developer audience.
1. Pick the target language block (Python / JavaScript / Java) and adapt the client init.
2. Replace "your_key" with an environment-variable read; never hardcode credentials.
3. Keep the Key Patterns invariant: constructor auth, async I/O, error handling, type safety.
4. Mirror method names across languages so the examples stay consistent.
Primary 8F verb: PRODUCE (this card is the output template a builder fills per language).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_sdk_example]] | downstream | 0.54 |
| [[bld_config_sdk_example]] | downstream | 0.48 |
| [[bld_collaboration_sdk_example]] | downstream | 0.47 |
| [[p01_kc_competitor_openai_sdk]] | sibling | 0.43 |
| [[sdk-example-builder]] | downstream | 0.38 |
