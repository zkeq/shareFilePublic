/**
 * 格式化文件大小
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的文件大小字符串
 */
export const formatFileSize = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
};

// MIME类型到友好显示名称的映射
const mimeTypeMap: { [key: string]: string } = {
  // 压缩文件
  'application/x-zip-compressed': 'ZIP',
  'application/zip': 'ZIP',
  'application/x-rar-compressed': 'RAR',
  'application/x-7z-compressed': '7Z',
  'application/gzip': 'GZ',
  'application/x-tar': 'TAR',
  'application/x-bzip': 'BZ',
  'application/x-bzip2': 'BZ2',
  
  // 可执行文件
  'application/x-msdownload': 'EXE',
  'application/x-executable': 'EXE',
  'application/x-msi': 'MSI',
  'application/x-apple-diskimage': 'DMG',
  'application/vnd.android.package-archive': 'APK',
  
  // 文档
  'application/pdf': 'PDF',
  'application/rtf': 'RTF',
  'application/msword': 'Word',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
  'application/vnd.ms-excel': 'Excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
  'application/vnd.ms-powerpoint': 'PowerPoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'application/vnd.oasis.opendocument.text': 'ODT',
  'application/vnd.oasis.opendocument.spreadsheet': 'ODS',
  'application/vnd.oasis.opendocument.presentation': 'ODP',
  'application/epub+zip': 'EPUB',
  'application/x-iwork-pages-sffpages': 'Pages',
  'application/x-iwork-numbers-sffnumbers': 'Numbers',
  'application/x-iwork-keynote-sffkey': 'Keynote',
  
  // 图片
  'image/jpeg': 'JPEG',
  'image/png': 'PNG',
  'image/gif': 'GIF',
  'image/webp': 'WebP',
  'image/svg+xml': 'SVG',
  'image/bmp': 'BMP',
  'image/tiff': 'TIFF',
  'image/x-icon': 'ICO',
  'image/vnd.adobe.photoshop': 'PSD',
  'image/heic': 'HEIC',
  'image/avif': 'AVIF',
  
  // 音频
  'audio/mpeg': 'MP3',
  'audio/wav': 'WAV',
  'audio/ogg': 'OGG',
  'audio/midi': 'MIDI',
  'audio/x-m4a': 'M4A',
  'audio/aac': 'AAC',
  'audio/flac': 'FLAC',
  'audio/x-ms-wma': 'WMA',
  'audio/webm': 'WebM Audio',
  'audio/x-aiff': 'AIFF',
  
  // 视频
  'video/mp4': 'MP4',
  'video/webm': 'WebM',
  'video/x-matroska': 'MKV',
  'video/quicktime': 'MOV',
  'video/x-msvideo': 'AVI',
  'video/x-ms-wmv': 'WMV',
  'video/mpeg': 'MPEG',
  'video/3gpp': '3GP',
  'video/x-flv': 'FLV',
  'video/ogg': 'OGV',
  
  // 文本和代码
  'text/plain': 'TXT',
  'text/html': 'HTML',
  'text/css': 'CSS',
  'text/javascript': 'JS',
  'text/markdown': 'MD',
  'text/x-python': 'Python',
  'text/x-java': 'Java',
  'text/x-c': 'C',
  'text/x-c++': 'C++',
  'text/x-ruby': 'Ruby',
  'text/x-php': 'PHP',
  'text/x-typescript': 'TypeScript',
  'text/csv': 'CSV',
  'text/xml': 'XML',
  'text/x-yaml': 'YAML',
  'application/json': 'JSON',
  'application/x-httpd-php': 'PHP',
  'application/xml': 'XML',
  'application/sql': 'SQL',
  
  // 字体
  'font/ttf': 'TTF',
  'font/otf': 'OTF',
  'font/woff': 'WOFF',
  'font/woff2': 'WOFF2',
  'application/vnd.ms-fontobject': 'EOT',
  
  // 3D和CAD
  'model/gltf-binary': 'GLB',
  'model/gltf+json': 'GLTF',
  'model/stl': 'STL',
  'model/obj': 'OBJ',
  'application/x-3ds': '3DS',
  'application/x-autocad': 'DWG',
  'application/dxf': 'DXF',
  'application/x-blender': 'BLEND',
  
  // 开发相关
  'application/x-git': 'GIT',
  'application/x-perl': 'Perl',
  'application/x-python': 'Python',
  'application/x-ruby': 'Ruby',
  'application/x-sh': 'Shell',
  'application/x-shellscript': 'Shell',
  'application/x-subrip': 'SRT',
  
  // 其他常见类型
  'application/x-bittorrent': 'Torrent',
  'application/vnd.docker.image.rootfs.diff.tar.gzip': 'Docker Layer',
  'application/x-virtualbox-vdi': 'VDI',
  'application/x-virtualbox-vmdk': 'VMDK',
  'application/x-iso9660-image': 'ISO',
  'application/pgp-signature': 'PGP Signature',
  'application/x-pkcs12': 'P12',
  'application/x-pkcs7-certificates': 'P7B',
  'application/x-x509-ca-cert': 'CRT'
};

/**
 * 将MIME类型转换为友好的显示名称
 * @param mimeType MIME类型字符串
 * @returns 友好的显示名称
 */
export const formatMimeType = (mimeType: string): string => {
  // 如果在映射表中存在，直接返回
  if (mimeType in mimeTypeMap) {
    return mimeTypeMap[mimeType];
  }

  // 如果是未知的MIME类型，尝试从文件扩展名获取类型
  if (mimeType.startsWith('application/')) {
    const subtype = mimeType.split('/')[1].toUpperCase();
    if (subtype !== 'OCTET-STREAM') {
      return subtype;
    }
  }

  // 对于其他类型，返回大写的主类型
  const [type] = mimeType.split('/');
  return type.toUpperCase();
};