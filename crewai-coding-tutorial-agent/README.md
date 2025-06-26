# Coding Tutorial Crew Workflow

```mermaid
graph TD
    A[Input:query] --> B(Coding tutorial agent);

    subgraph "Query search tools"
        T1[Sperper]
        T2[CrewaiWebScraper]
    end

    B -- Uses --> T1;
    B -- Uses --> T2;

    B -->|Performs| F{Web Scrawl Task};
    F -->|Performs| G{Scrape Websites Task};
    G -->|Performs| H{Generate Tutorial Task};
    H -->|Output| I(Final Tutorial);
```

This graph shows the initial `Input Query` get passed to the `Coding Tutorial Agent`, who then performs a web Crawl to gather relevant turoial links.

The `Coding Tutorial Agent` then Performs the `Scrape Website Task`, and uses the data as a knowledge base to perform the `Generate Tutorial Task` and create a tutorial based on the `Input Query`.

This tutorial is then returned as the `Final Tutorial`