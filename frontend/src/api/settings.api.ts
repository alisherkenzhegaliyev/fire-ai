import client from './client'

export interface NlpSettings {
  modelId: string
  concurrency: number
  availableModels: string[]
  availableConcurrency: number[]
}

export async function fetchNlpSettings(): Promise<NlpSettings> {
  const { data } = await client.get<NlpSettings>('/api/settings')
  return data
}

export async function updateNlpSettings(modelId: string, concurrency: number): Promise<void> {
  await client.post('/api/settings', { model_id: modelId, concurrency })
}
