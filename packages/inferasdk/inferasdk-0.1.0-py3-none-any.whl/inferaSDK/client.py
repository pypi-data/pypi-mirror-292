import aiohttp
import asyncio

class InferaSDK:
    def __init__(self, api_key, base_url="https://api.infera.org"):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api_key": self.api_key
        }

    # submit a job and get a reciept back for the submitted job
    async def submit_job(self, session, model, messages, max_output, temperature):
        url = f"{self.base_url}/submit_job"
        payload = {
            "model": model,
            "messages": messages,
            "max_output": max_output,
            "temperature": temperature
        }
        async with session.post(url, json=payload, headers=self.headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return f"Error: {response.status}, {await response.text()}"

    # retrieve results using reciept 
    async def get_result(self, session, job_id):
        url = f"{self.base_url}/get_result/{job_id}"
        async with session.get(url, headers=self.headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return f"Error: {response.status}, {await response.text()}"

    async def process_job(self, session, model, messages, max_output, temperature):
        # Submit the job
        job_result = await self.submit_job(session, model, messages, max_output, temperature)
        print("Job submitted:", job_result)

        if isinstance(job_result, dict) and 'job_id' in job_result:
            job_id = job_result['job_id']
            
            start_time = asyncio.get_event_loop().time()
            
            # Poll for results
            while True:
                result = await self.get_result(session, job_id)
                if isinstance(result, dict):
                    if 'result' in result and 'message' in result['result']:
                        print(f"Job {job_id} completed.")
                        return result['result']['message'].get('content', 'No content found')
                    elif result.get('status') == 'processing':
                        print(f"Job {job_id} still processing, waiting...")
                    else:
                        print(f"Job {job_id} - Unexpected response structure:")
                        print("Full response:", result)
                        return str(result)
                elif isinstance(result, str) and result.startswith("Error"):
                    print(f"Job {job_id} - Error occurred, retrying in 5 seconds:", result)
                else:
                    print(f"Job {job_id} - Unexpected result type:", type(result))
                    print("Full response:", result)
                    return str(result)
                
                # Check if 60 seconds have passed
                if asyncio.get_event_loop().time() - start_time > 60:
                    print(f"Job {job_id} - Timeout: Retrieval took more than 60 seconds.")
                    return f"Timeout: Job {job_id} retrieval exceeded 60 seconds"
                
                await asyncio.sleep(5)  # Wait for 5 seconds before checking again
        else:
            print("Failed to submit job:", job_result)
            return None

