import json
from typing import List, Dict, Optional
import asyncio
import os

class SupabaseClient:
    def __init__(self):
        self.url = "https://your-project-ref.supabase.co"
        self.key = "your-anon-or-service-role-key"
        
        try:
            from platform import window
            window.eval("window.crabpy_fetch_result = null;")
            self.has_window = True
        except:
            self.has_window = False
            print("Warning: Running without browser window (probably desktop mode)")

    async def _fetch(self, url: str, method: str = "GET", data: dict = None) -> dict:
        
        if not self.has_window:
            return {"error": "No browser window available"}
        
        try:
            from platform import window
            
            if method == "GET":
                js_code = f"""
                window.crabpy_fetch_result = null;
                fetch('{url}', {{
                    method: '{method}',
                    headers: {{
                        'apikey': '{self.key}',
                        'Authorization': 'Bearer {self.key}',
                        'Content-Type': 'application/json'
                    }}
                }})
                .then(response => {{
                    console.log('Response status:', response.status);
                    console.log('Response headers:', response.headers);
                    if (!response.ok) {{
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }}
                    
                    // Check if response has content
                    const contentLength = response.headers.get('content-length');
                    if (contentLength === '0' || response.status === 204) {{
                        // No content, return success indicator
                        window.crabpy_fetch_result = {{ success: true, data: {{ created: true }} }};
                        return;
                    }}
                    
                    return response.json();
                }})
                .then(data => {{
                    if (data !== undefined) {{
                        console.log('Success:', data);
                        window.crabpy_fetch_result = {{ success: true, data: data }};
                    }}
                }})
                .catch(error => {{
                    console.error('Fetch error:', error);
                    window.crabpy_fetch_result = {{ success: false, error: error.toString() }};
                }});
                """
            else:
                if data:
                    json_str = json.dumps(data)
                    js_code = f"""
                    window.crabpy_fetch_result = null;
                    const requestData = {json_str};
                    console.log('Sending POST data:', requestData);
                    
                    fetch('{url}', {{
                        method: '{method}',
                        headers: {{
                            'apikey': '{self.key}',
                            'Authorization': 'Bearer {self.key}',
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(requestData)
                    }})
                    .then(response => {{
                        console.log('Response status:', response.status);
                        console.log('Response ok:', response.ok);
                        
                        if (!response.ok) {{
                            return response.text().then(text => {{
                                console.log('Error response body:', text);
                                throw new Error('HTTP ' + response.status + ': ' + response.statusText + ' - ' + text);
                            }});
                        }}
                        
                        // Check if response has content
                        const contentType = response.headers.get('content-type');
                        const contentLength = response.headers.get('content-length');
                        
                        console.log('Content-Type:', contentType);
                        console.log('Content-Length:', contentLength);
                        
                        if (contentLength === '0' || response.status === 201 || response.status === 204) {{
                            // POST success with no content (common for INSERT operations)
                            console.log('Success: No content response');
                            window.crabpy_fetch_result = {{ success: true, data: {{ created: true, status: response.status }} }};
                            return null;
                        }}
                        
                        if (contentType && contentType.includes('application/json')) {{
                            return response.json();
                        }} else {{
                            return response.text();
                        }}
                    }})
                    .then(data => {{
                        if (data !== null && data !== undefined) {{
                            console.log('Success with data:', data);
                            window.crabpy_fetch_result = {{ success: true, data: data }};
                        }}
                        // If data is null, success was already set above
                    }})
                    .catch(error => {{
                        console.error('Fetch error:', error);
                        window.crabpy_fetch_result = {{ success: false, error: error.toString() }};
                    }});
                    """
                else:
                    js_code = f"""
                    window.crabpy_fetch_result = null;
                    fetch('{url}', {{
                        method: '{method}',
                        headers: {{
                            'apikey': '{self.key}',
                            'Authorization': 'Bearer {self.key}',
                            'Content-Type': 'application/json'
                        }}
                    }})
                    .then(response => {{
                        if (!response.ok) {{
                            throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                        }}
                        
                        const contentLength = response.headers.get('content-length');
                        if (contentLength === '0' || response.status === 204) {{
                            window.crabpy_fetch_result = {{ success: true, data: {{ updated: true }} }};
                            return;
                        }}
                        
                        return response.json();
                    }})
                    .then(data => {{
                        if (data !== undefined) {{
                            window.crabpy_fetch_result = {{ success: true, data: data }};
                        }}
                    }})
                    .catch(error => {{
                        window.crabpy_fetch_result = {{ success: false, error: error.toString() }};
                    }});
                    """
            
            print(f"Executing JavaScript for {method} {url}")
            if data:
                print(f"Data: {data}")
            
            window.eval(js_code)
            
            # Poll for result (wait up to 10 seconds)
            for i in range(100):  # 100 * 0.1 = 10 seconds max
                await asyncio.sleep(0.1)
                
                try:
                    result_str = window.eval("JSON.stringify(window.crabpy_fetch_result)")
                    if result_str and result_str != "null" and result_str != "undefined":
                        result = json.loads(result_str)
                        
                        # Clear the result
                        window.eval("window.crabpy_fetch_result = null;")
                        
                        if result.get("success"):
                            print(f"Success: {result.get('data', {})}")
                            return result.get("data", {})
                        else:
                            print(f"Error: {result.get('error', 'Unknown error')}")
                            return {"error": result.get("error", "Unknown error")}
                except Exception as parse_error:
                    print(f"Parse error: {parse_error}")
                    continue
            
            print("Request timeout")
            return {"error": "Request timeout"}
            
        except Exception as e:
            print(f"Fetch error: {e}")
            return {"error": str(e)}

    async def submit_score(self, initials: str, score: int, crabs_caught: int, drunk_bonus: int) -> bool:
        try:
            data = {
                "initials": initials.upper()[:3], 
                "score": score,
                "crabs_caught": crabs_caught,
                "drunk_bonus": drunk_bonus,
            }
            
            result = await self._fetch(
                f"{self.url}/rest/v1/highscores",
                method="POST",
                data=data
            )
            
            success = "error" not in result and (result.get("created") or result.get("data"))
            print(f"Submit score result: {success}, response: {result}")
            return success
            
        except Exception as e:
            print(f"Error submitting score: {e}")
            return False
    
    async def get_top_scores(self, limit: int = 10) -> List[Dict]:
        try:
            url = f"{self.url}/rest/v1/highscores?select=*&order=score.desc&limit={limit}"
            result = await self._fetch(url)
            
            if "error" in result:
                print(f"Error in get_top_scores: {result['error']}")
                return []
            
            scores = result if isinstance(result, list) else []
            print(f"Retrieved {len(scores)} scores")
            return scores
            
        except Exception as e:
            print(f"Error fetching scores: {e}")
            return []
    
    async def get_existing_score(self, initials: str) -> Optional[Dict]:
        try:
            url = f"{self.url}/rest/v1/highscores?select=*&initials=eq.{initials.upper()}"
            result = await self._fetch(url)
            
            if "error" in result or not isinstance(result, list):
                return None
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"Error fetching existing score: {e}")
            return None
    
    async def update_score(self, initials: str, score: int, crabs_caught: int, drunk_bonus: int) -> bool:
        try:
            data = {
                "score": score,
                "crabs_caught": crabs_caught,
                "drunk_bonus": drunk_bonus,
            }
            
            url = f"{self.url}/rest/v1/highscores?initials=eq.{initials.upper()}"
            result = await self._fetch(url, method="PATCH", data=data)
            
            return "error" not in result
            
        except Exception as e:
            print(f"Error updating score: {e}")
            return False
    
    async def is_high_score(self, score: int) -> bool:
        try:
            url = f"{self.url}/rest/v1/highscores?select=score&order=score.desc&limit=10"
            result = await self._fetch(url)
            
            if "error" in result or not isinstance(result, list):
                print(f"Error checking high score, assuming True: {result}")
                return True
            
            score_values = [row["score"] for row in result if "score" in row]
            
            if len(score_values) < 10:
                return True
            
            is_high = score > min(score_values)
            print(f"High score check: {score} > {min(score_values)} = {is_high}")
            return is_high
            
        except Exception as e:
            print(f"Error checking high score: {e}")
            return True
    
    async def submit_or_update_score(self, initials: str, score: int, crabs_caught: int, drunk_bonus: int):
        try:
            initials = initials.upper()[:3]
            existing = await self.get_existing_score(initials)
            
            if existing:
                if score > existing["score"]:
                    success = await self.update_score(initials, score, crabs_caught, drunk_bonus)
                    if success:
                        return True, f"New high score! Previous: {existing['score']}"
                    else:
                        return False, "Failed to update score"
                else:
                    return False, f"Score too low! Your best: {existing['score']}"
            else:
                success = await self.submit_score(initials, score, crabs_caught, drunk_bonus)
                if success:
                    return True, "New player registered!"
                else:
                    return False, "Failed to submit score"
                    
        except Exception as e:
            print(f"Error in submit_or_update_score: {e}")
            return False, "Network error"

    # Synchronous wrappers for backward compatibility
    def submit_score_sync(self, initials: str, score: int, crabs_caught: int, drunk_bonus: int) -> bool:
        print(f"Sync submit requested: {initials} - {score}")
        return True  # Assume success for now
    
    def get_top_scores_sync(self, limit: int = 10) -> List[Dict]:
        return []
    
    def is_high_score_sync(self, score: int) -> bool:
        return score > 100

# Global instance
supabase_client = SupabaseClient()