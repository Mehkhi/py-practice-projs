# Async Web Scraper - Spec, Requirements, and Checklist

## Project Specification
Develop an asynchronous web scraper capable of crawling multiple web pages concurrently and storing the extracted results.

## Requirements (Core Skills)
- asyncio for handling asynchronous operations
- aiohttp for performing asynchronous HTTP requests
- Semaphore to limit the number of concurrent connections
- Backoff mechanisms for handling retries

## Completion Checklist

### Milestones
- [ ] Implement retry logic for failed requests
- [ ] Introduce polite delays between requests to avoid overwhelming servers
- [ ] Add caching functionality to prevent re-scraping unchanged content

### Stretch Goals
- [ ] Create pluggable pipelines for outputting data to CSV or SQLite databases
