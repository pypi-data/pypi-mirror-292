import mimetypes
import gzip
import io
import tarfile
import zipfile


print(mimetypes.guess_type('/home/fmeyer/tmp/test/test.fasta'))
print('.zip\t', mimetypes.guess_type('/home/fmeyer/tmp/test.zip'))
print('.gz\t', mimetypes.guess_type('/home/fmeyer/tmp/test.gz')) # gzip.open
print('tar.gz\t', mimetypes.guess_type('/home/fmeyer/tmp/test.tar.gz'))


def open_generic(file):
    file_type, file_encoding = mimetypes.guess_type(file)

    if file_encoding == 'gzip':
        if file_type == 'application/x-tar':  # .tar.gz
            tar = tarfile.open(file, 'r:gz')
            f = tar.extractfile(tar.getmembers()[0])
            return io.TextIOWrapper(f)
        else:  # .gz
            return gzip.open(file, 'rt')
    if file_type == 'application/zip':  # .zip
        f = zipfile.ZipFile(file, 'r')
        f = f.open(f.namelist()[0])
        return io.TextIOWrapper(f)
    else:
        return open(file, 'rt')


ff = None
with open_generic('/home/fmeyer/tmp/test/test.fasta.gz') as ff:
    for line in ff:
        print(line, end='')
    #     break
    # print(ff.closed)

print(ff.closed)
