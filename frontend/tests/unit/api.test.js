import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { apiFetch, errorMessage, navigation } from '../../js/shared/api.js';

const json = (status, body = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

let fetchMock;
beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
  navigation.toLogin = vi.fn();
});
afterEach(() => vi.unstubAllGlobals());

const calledPaths = () => fetchMock.mock.calls.map(([path]) => path);

describe('apiFetch', () => {
  it('envía JSON con las cookies del mismo origen', async () => {
    fetchMock.mockResolvedValueOnce(json(200));

    await apiFetch('/api/v1/x', { method: 'POST', json: { a: 1 } });

    const [, options] = fetchMock.mock.calls[0];
    expect(options.credentials).toBe('same-origin');
    expect(options.headers['Content-Type']).toBe('application/json');
    expect(options.body).toBe('{"a":1}');
  });

  it('ante 401 renueva la sesión una vez y reintenta', async () => {
    fetchMock
      .mockResolvedValueOnce(json(401))
      .mockResolvedValueOnce(json(200))
      .mockResolvedValueOnce(json(200, { ok: true }));

    const response = await apiFetch('/api/v1/auth/me');

    expect(await response.json()).toEqual({ ok: true });
    expect(calledPaths()).toEqual(['/api/v1/auth/me', '/api/v1/auth/refresh', '/api/v1/auth/me']);
    expect(navigation.toLogin).not.toHaveBeenCalled();
  });

  it('si la renovación falla, va al login sin reintentar', async () => {
    fetchMock.mockResolvedValueOnce(json(401)).mockResolvedValueOnce(json(401));

    const response = await apiFetch('/api/v1/auth/me');

    expect(response.status).toBe(401);
    expect(calledPaths()).toEqual(['/api/v1/auth/me', '/api/v1/auth/refresh']);
    expect(navigation.toLogin).toHaveBeenCalledOnce();
  });

  it('dos 401 a la vez comparten una sola renovación', async () => {
    fetchMock.mockImplementation(async (path) => {
      if (path === '/api/v1/auth/refresh') return json(200);
      return fetchMock.mock.calls.filter(([p]) => p === path).length === 1 ? json(401) : json(200);
    });

    await Promise.all([apiFetch('/api/v1/a'), apiFetch('/api/v1/b')]);

    expect(calledPaths().filter((p) => p === '/api/v1/auth/refresh')).toHaveLength(1);
  });

  it('otros errores pasan tal cual', async () => {
    fetchMock.mockResolvedValueOnce(json(403));

    expect((await apiFetch('/api/v1/x')).status).toBe(403);
    expect(fetchMock).toHaveBeenCalledOnce();
  });
});

describe('errorMessage', () => {
  it('toma el mensaje del formato único de errores', async () => {
    const response = json(423, { errors: [{ field: null, code: 'x', message: 'Bloqueada' }] });
    expect(await errorMessage(response)).toBe('Bloqueada');
  });

  it('da un mensaje genérico si la respuesta no trae errores', async () => {
    expect(await errorMessage(new Response('boom', { status: 500 }))).toMatch(/inesperado/);
  });
});
