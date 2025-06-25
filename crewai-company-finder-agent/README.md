# Company Finder Crew Workflow

This diagram illustrates the workflow of the Company Finder Crew, detailing the agents, tasks, and the flow of information.

```mermaid
graph TD
    A[Input: Company Search] --> CA(Crawler Agent: Search crawler and URL retriever);

    subgraph "Web Scraping Tools"
        T1[SerperWebCrawler]
        T2[WebsiteScraper]
        T3[CrunchbaseSearcher]
        T4[ContactPageCrawler]
    end

    CA -- Uses --> T1;
    SA -- Performs --> WBT{Web Crawler Task};

    WBT -- Returned URLS --> UV(Url Validator agent: URL scraper and analyser);
    UV -- Uses --> T2;
    UV -- Performs --> WST{Web Scraping Task};

    WST -- Companys and Contacts --> CS(Crunchbase Search Agent:Contact retriever from crunchbase snippets);
    

    CS -- Uses --> T3;
    CS -- Performs CCT{Crunchbase Crawling Task};

    CCT -- Companies and Updated Contacts --> CPC(Contact Page Crawler Agent:Contact page crawler and scraper);

    CPC -- Uses --> T1;
    CPC -- Uses --> T2;

    CPC -- Performs --> CPS{Contact Page Crawling and Scraping Task};
    CSP -- Company and Updated Contacts --> FL[Output: Final Company and Contacts List];
    
```

This graph shows the initial input (Website URL) going to the `Scraper Agent`. This agent uses its specialized tools to perform the `Data Collection Task`. The output of this task (Collected Data & Metrics) is then passed to the `Analyse Agent`, which performs the `Analysis Task`. The resulting `Analysis Report` is then used by the `Optimization Agent` to perform the `Optimization Task`, which finally produces the `Final SEO Report`.