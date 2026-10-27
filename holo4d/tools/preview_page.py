"""Local range-enabled preview; not an Internet-facing production server."""
import argparse
import functools
import http.server
import mimetypes
from pathlib import Path


def byte_range(value, size):
    if not value.startswith('bytes=') or ',' in value or size == 0:
        raise ValueError('Only one byte range is supported')
    left, right = value[6:].split('-', 1)
    if not left:
        count = int(right)
        if count < 1:
            raise ValueError('Invalid suffix range')
        return max(0, size-count), size-1
    start = int(left)
    end = min(int(right), size-1) if right else size-1
    if start < 0 or start >= size or end < start:
        raise ValueError('Unsatisfiable range')
    return start, end


class MediaHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path))
        self.revalidate = not path.is_file() or path.suffix.lower() not in {'.mp4', '.jpg', '.png', '.svg'}
        if self.revalidate:
            return super().send_head()
        stat = path.stat()
        size = stat.st_size
        tag = f'"{stat.st_mtime_ns:x}-{size:x}"'
        if self.headers.get('If-None-Match') == tag and not self.headers.get('Range'):
            self.send_response(304)
            self.send_header('ETag', tag)
            self.end_headers()
            return None
        start, end, status = 0, size-1, 200
        requested = self.headers.get('Range')
        if requested:
            try:
                start, end = byte_range(requested, size)
            except (ValueError, TypeError):
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return None
            status = 206
        try:
            handle = path.open('rb')
        except OSError:
            self.send_error(404)
            return None
        handle.seek(start)
        self.remaining = end-start+1
        self.send_response(status)
        self.send_header('Content-Type', mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(self.remaining))
        self.send_header('ETag', tag)
        self.send_header('Last-Modified', self.date_time_string(stat.st_mtime))
        self.send_header('Cache-Control', 'public, max-age=3600')
        if status == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        return handle

    def end_headers(self):
        if getattr(self, 'revalidate', False):
            self.send_header('Cache-Control', 'no-cache')  # Page edits show on a plain reload.
        super().end_headers()

    def copyfile(self, source, outputfile):
        if self.remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self.remaining
        try:
            while remaining > 0:
                data = source.read(min(65536, remaining))
                if not data:
                    break
                outputfile.write(data)
                remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Browser cancelled an offscreen request.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    handler = functools.partial(MediaHandler, directory=str(args.directory.resolve()))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    print(f'Local preview: http://127.0.0.1:{server.server_port}/ (SSH forward this port)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
