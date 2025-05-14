# SEO Analysis Crew Workflow

This diagram illustrates the workflow of the SEO Analysis Crew, detailing the agents, tasks, and the flow of information.

```mermaid
graph TD
    A[Input: Website URL] --> SA(Scraper Agent: SEO Technical Auditor and Data Collector);

    subgraph "Data Collection Tools"
        T1[BrowserlessScraper]
        T2[LoadingTimeTracker]
        T3[MobileOptimizationTool]
        T4[SubpageAnalyzer]
    end

    SA -- Uses --> T1;
    SA -- Uses --> T2;
    SA -- Uses --> T3;
    SA -- Uses --> T4;

    SA -- Performs --> DCT{Data Collection Task};
    DCT -- Collected Data & Metrics --> AA(Analyse Agent: SEO Analytics and Insights Specialist);
    AA -- Performs --> AT{Analysis Task};
    AT -- Analysis Report --> OA(Optimization Agent: SEO Strategy and Implementation Expert);
    OA -- Performs --> OT{Optimization Task};
    OT -- Optimization Plan --> FR[Output: Final SEO Report];
```

This graph shows the initial input (Website URL) going to the `Scraper Agent`. This agent uses its specialized tools to perform the `Data Collection Task`. The output of this task (Collected Data & Metrics) is then passed to the `Analyse Agent`, which performs the `Analysis Task`. The resulting `Analysis Report` is then used by the `Optimization Agent` to perform the `Optimization Task`, which finally produces the `Final SEO Report`.
