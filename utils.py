import aiohttp
import aiofiles

def translate_day_to_french(day_name):
    days_translation = {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche'
    }
    return days_translation.get(day_name, None)

async def download_file(url: str, save_as: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(save_as, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            await file.write(chunk)
                    print(f"Le fichier a été téléchargé et sauvegardé sous le nom '{save_as}'.")
                else:
                    print(f"Échec du téléchargement. Code de statut HTTP: {response.status}")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

