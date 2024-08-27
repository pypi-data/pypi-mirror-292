import asyncio
import aiohttp
from inferaSDK import InferaSDK

async def main():
    api_key = "79f894a9-5b60-4eb5-bdb0-e8fdd1164186"  # Replace with your actual API key
    sdk = InferaSDK(api_key)
    max_output = 400
    models = ["llama3.1:latest", "dolphin-mistral:latest", "mistral:latest", "llama3.1:latest"]
    messages = [
        [{"role": "user", "content": "what is the difference between 4000 cows and 3000 cows?"}],
        [{"role": "user", "content": "give me a list of girl names to name my baby that are greek or italian sounding"}],
        [{"role": "user", "content": "what does it mean to be a milk drinker?"}],
        [{"role": "user", "content": "I enjoy eating celery, give me some recipes for using celery"}]
    ]
    temperatures = [0.7, 0.5, 0.3, 0.8, 0.6, 0.4, 0.2, 0.9]

    async with aiohttp.ClientSession() as session:
        # Submit jobs concurrently with custom max_output and temperature
        tasks = [
            sdk.process_job(session, models[i % 4], messages[i % 4], max_output, temperature)
            for i, temperature in enumerate(temperatures)
        ]
        results = await asyncio.gather(*tasks)

        print("\nFinal results:")
        for i, result in enumerate(results, 1):
            print(f"\nJob {i} result:")
            print(result)

if __name__ == "__main__":
    asyncio.run(main())