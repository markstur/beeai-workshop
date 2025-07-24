
from beeai_framework.tools.mcp import MCPTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, Any, Optional, List
import os
import asyncio
import json
import re
import logging
from pathlib import Path

#Ensure that your path is set to the current folder so that the proper enviorment variables are found 
print(f"Current working directory: {os.getcwd()}")
script_dir = Path(__file__).parent
print(f"Script directory: {script_dir}")
os.chdir(script_dir)
print(f"Changed to: {os.getcwd()}")

# Set up logging to see what's happening when the tool is called
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set settings (enviorment variables)
class Settings(BaseSettings):
    TAVILY_API_KEY: str = Field(alias='TAVILY_API_KEY')
    model_config = SettingsConfigDict(env_file='.env')

# Create a helper function to parse the Tavily Result in Structured Format and returns the urls, text results, and number of results
def parse_search_results(text_content: str, query: str) -> Dict[str, Any]:
    """Parse Tavily text results into structured format"""
    results = []
    
    # Split by "Title:" to get individual results
    title_sections = text_content.split("Title:")
    
    for section in title_sections[1:]:  # Skip first empty section
        lines = section.strip().split('\n')
        title = lines[0].strip() if lines else ""
        
        url = ""
        content = ""
        
        for i, line in enumerate(lines):
            if line.startswith("URL:"):
                url = line.replace("URL:", "").strip()
            elif line.startswith("Content:"):
                content_lines = lines[i:]
                content = " ".join(line.replace("Content:", "").strip() 
                                for line in content_lines if line.strip())
                break
        
        if title and url:
            results.append({
                "title": title,
                "url": url,
                "content": content.strip(),
                "score": 1.0 - (len(results) * 0.1)
            })
    
    return {
        "query": query,
        "results": results,
        "total_results": len(results)
    }

#Create the class that actually starts and initalizes the tavily MCP server locally, does the search, and handles the clean shut down of the session and server
class TavilySearch:
    """Tavily search client with persistent MCP session"""
    
    def __init__(self):
        self.settings = Settings()
        self.session = None
        self.search_tool = None
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "tavily-mcp@latest"],
            env={"TAVILY_API_KEY": self.settings.TAVILY_API_KEY}
        )
        self._context_manager = None
    
    async def __aenter__(self):
        """Start MCP server and initialize session"""
        self._context_manager = stdio_client(self.server_params)
        read, write = await self._context_manager.__aenter__()
        
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        # Get search tool once
        tools = await MCPTool.from_client(self.session)
        self.search_tool = next((tool for tool in tools if "tavily-search" in tool.name), None)
        
        if not self.search_tool:
            raise ValueError("Tavily search tool not found")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up session and server"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._context_manager:
            await self._context_manager.__aexit__(exc_type, exc_val, exc_tb)
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = False,
        include_domains: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform search using existing session
        
        Args:
            query: Search query
            max_results: Number of results to return
            search_depth: "basic" or "advanced"
            include_answer: Include AI-generated answer
            include_domains: List of domains to include
            **kwargs: Additional search parameters
        
        Returns:
            Structured search results
        """
        if not self.session or not self.search_tool:
            raise RuntimeError("TavilySearch not initialized. Use 'async with TavilySearch():'")
        
        try:
            # Prepare search arguments
            arguments = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_images": False,
                "topic": "general",
                "include_answer": include_answer,
                "include_raw_content": False
            }
            
            if include_domains:
                arguments["include_domains"] = include_domains
            
            # Add any additional parameters
            arguments.update(kwargs)
            
            # Execute search
            result = await self.search_tool.run(arguments)
            
            # Extract text content from JSONToolOutput (complex nested structure)
            # Convert JSONToolOutput to string, then parse as JSON to get nested data
            result_str = str(result)
            result_data = [{"type": "text", "text": result_str}]  # Fallback structure
            
            # Try to parse the nested JSON structure
            try:
                # The result string looks like: [{"type": "text", "text": "..."}]
                import ast
                try:
                    result_data = ast.literal_eval(result_str)
                except:
                    # Fallback: create the expected structure
                    result_data = [{"type": "text", "text": result_str}]
                
                # Extract the text field which contains another JSON string
                if isinstance(result_data, list) and len(result_data) > 0:
                    first_item = result_data[0]
                    if isinstance(first_item, dict) and "text" in first_item:
                        nested_text = first_item["text"]
                        
                        # Parse the nested JSON to get the actual search results
                        nested_data = json.loads(nested_text)
                        if isinstance(nested_data, list) and len(nested_data) > 0:
                            nested_item = nested_data[0]
                            if isinstance(nested_item, dict) and "text" in nested_item:
                                text_content = nested_item["text"]
                            else:
                                text_content = nested_text
                        else:
                            text_content = nested_text
                    else:
                        text_content = str(result)
                else:
                    text_content = str(result)
                    
            except Exception as parse_error:
                # If all parsing fails, convert result to string and try to extract content
                text_content = str(result)
            
            # Parse and return structured results
            return parse_search_results(text_content, query)
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

# This is a function that can search multiple queries in one Tavily Search Call
async def search_multiple_queries(queries: List[str], **search_kwargs) -> Dict[str, Dict[str, Any]]:
    """Search multiple queries efficiently using one session"""
    results = {}
    
    async with TavilySearch() as tavily:
        for query in queries:
            results[query] = await tavily.search(query, **search_kwargs)
    
    return results


# To Test the Tavily Search Tool with it's different settings (basic, with AI Answer, advanced domains) and Searching Multiple queries in on search call run the following:
async def main():
    """Example usage showing efficient session reuse"""
    
    # Single session for multiple searches
    async with TavilySearch() as tavily:
        print("=== Multiple Searches with One Session ===")
        
        # Basic search
        results1 = await tavily.search("Python async programming", max_results=3)
        print(f"Query 1: Found {len(results1.get('results', []))} results")
        
        # Search with answer
        results2 = await tavily.search("AI developments 2024", include_answer=True, max_results=3)
        print(f"Query 2: Found {len(results2.get('results', []))} results")
        
        # Advanced search with domains
        results3 = await tavily.search(
            "machine learning tutorials",
            search_depth="advanced",
            include_domains=["github.com", "medium.com"],
            max_results=5
        )
        print(f"Query 3: Found {len(results3.get('results', []))} results")
        
        # Display first result from each
        for i, results in enumerate([results1, results2, results3], 1):
            if results.get('results'):
                first_result = results['results'][0]
                print(f"\nFirst result from query {i}:")
                print(f"  {first_result['title']}")
                print(f"  {first_result['url']}")
    
    # Batch search convenience function
    print("\n=== Batch Search ===")
    batch_queries = [
        "Python tutorials", 
        "JavaScript frameworks", 
        "React best practices"
    ]
    
    batch_results = await search_multiple_queries(batch_queries, max_results=2)
    
    for query, results in batch_results.items():
        count = len(results.get('results', []))
        print(f"{query}: {count} results")


if __name__ == "__main__":
    asyncio.run(main())
