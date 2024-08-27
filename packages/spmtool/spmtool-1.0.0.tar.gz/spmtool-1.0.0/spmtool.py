#!/usr/bin/python3
# SPDX-License-Identifier: MIT
"""spmtool

Read/write SPM motor controller configuration over serial connection

Based on Kelly Controller Configuration software version '4.5'
and brushed motor controller model: SPM24121. Example usage:

Test serial connection:

	$ spmtool

Read controller settings into conf.bin using SPM24121 preset:

	$ spmtool -r -s SPM24121 conf.bin

Write settings from conf.bin to controller using SPM24121 preset:

	$ spmtool -w -s SPM24121 conf.bin

Compare controller memory with contents of conf.bin using SPM24121 preset:

	$ spmtool -c -s SPM24121 conf.bin

"""

import sys
import logging
import argparse
from serial import Serial

# Constants
_BAUDRATE = 19200
_MEM_LEN = 0x80
_PACK_LEN = 0x10
_CMD_SWVER = 0x11
_CMD_PING = 0xf1
_CMD_GET = 0xf2
_CMD_SET = 0xf3
_CMD_COMMIT = 0xf4
_MASKS = {
    'SPM24121': {
        0x00: 0x2f,
        0x01: 0x7f,
        0x02: 0xff,
        0x03: 0xff,
        0x04: 0xff,
        0x05: 0xff,
        0x0c: 0xff,
        0x0e: 0xff,
        0x0f: 0xff,
        0x10: 0xff,
        0x11: 0xff,
        0x12: 0xff,
        0x13: 0xff,
        0x14: 0xff,
        0x15: 0xff,
        0x1c: 0xff,
        0x1e: 0xff,
        0x21: 0xff,
        0x22: 0xff,
        0x26: 0xff,
        0x27: 0xff,
        0x28: 0xff,
        0x29: 0xff,
        0x2a: 0xff,
        0x2b: 0xff,
        0x2c: 0xff,
        0x2d: 0xff,
        0x3d: 0xff,
        0x3e: 0xff,
        0x3f: 0xff,
        0x64: 0xff,
    }
}

_log = logging.getLogger('spmtool')


class Spm():
    """SPM motor controller config object"""

    def __init__(self, port=None):
        self._memory = bytearray(_MEM_LEN)
        self._config = bytearray(_MEM_LEN)
        self._mask = bytearray(_MEM_LEN)
        self._port = None
        self._swver = None
        self.port = port

    def info(self):
        """Print controller info to stdout"""
        swver = 'n/a'
        if self._swver is not None:
            swver = self._swver
        model = 'n/a'
        serno = 'n/a'
        if self._memory[0x40] != 0x00:
            model = self._memory[0x40:0x48].decode('utf-8', 'replace')
            serno = self._memory[0x4c:0x50].hex()
        print('S/W VER:', swver)
        print('Model:', model)
        print('Serial:', serno)

    def load(self, filename):
        """Load controller memory from file"""
        with open(filename, 'rb') as f:
            sz = f.readinto(self._config)
            if sz != _MEM_LEN:
                _log.warning('Short read %d < %d bytes from config file', sz,
                             _MEM_LEN)
            else:
                _log.debug('Read %d bytes from config file', sz)

    def loadmask(self, settings):
        """Read settings mask from preset or file"""
        count = 0
        if settings in _MASKS:
            _log.debug('Loading mask from preset %s', settings)
            sm = _MASKS[settings]
            for offset in sm:
                self._mask[offset] = sm[offset]
                count += 1
        else:
            _log.debug('Loading mask from file %s', settings)
            with open(settings, 'r') as f:
                count = 0
                for l in f:
                    lv = l.split(maxsplit=2)
                    if len(lv) > 2 and lv[0] and lv[0].startswith('0x'):
                        try:
                            offset = int(lv[0], 16)
                            mask = int(lv[1], 16)
                            if offset < _MEM_LEN:
                                self._mask[offset] |= mask
                                count += 1
                            else:
                                _log.debug('Offset too large: %d', offset)
                        except Exeption:
                            _log.debug('Skipped invalid settings mask: %r', lv)
        _log.debug('Loaded %d settings from %s', count, settings)

    def maskconf(self):
        """Apply settings mask to config"""
        offset = 0
        while offset < _MEM_LEN:
            self._config[offset] &= self._mask[offset]
            offset += 1

    def maskmem(self):
        """Apply settings mask to controller memory"""
        offset = 0
        while offset < _MEM_LEN:
            self._memory[offset] &= self._mask[offset]
            offset += 1

    def mergeconf(self):
        """Merge masked config bits with controller memory"""
        offset = 0
        while offset < _MEM_LEN:
            if self._mask[offset]:
                mask = self._mask[offset]
                invmask = mask ^ 0xff
                cval = self._memory[offset] & (mask ^ 0xff)
                mval = self._config[offset] & mask
                self._memory[offset] = cval | mval
            offset += 1

    def save(self, filename):
        """Save config to file"""
        with open(filename, 'wb') as f:
            sz = f.write(self._config)
            _log.debug('Wrote %d bytes to file', sz)

    def commit(self):
        """Save changes on controller"""
        self._sendmsg(_CMD_COMMIT)
        return self._readmsg(_CMD_COMMIT, 0) is not None

    def setmem(self, offset, wlen):
        """Set wlen bytes at offset in controller"""
        plen = _PACK_LEN - 3
        data = self._memory[offset:offset + wlen]
        if wlen < plen:
            data += b'\xff' * (plen - wlen)
        subcmd = bytes((offset, plen, 0x00))
        self._sendmsg(_CMD_SET, subcmd + data)
        return self._readmsg(_CMD_SET, 1) is not None

    def write(self):
        """Write memory to controller"""
        if self._port is None:
            self.open()
        if self._port is None:
            _log.debug('Write aborted')
            return False

        offset = 0
        while offset < _MEM_LEN:
            wlen = min(_PACK_LEN - 3, _MEM_LEN - offset)
            if self.setmem(offset, wlen):
                _log.debug('SET %02x\t%s', offset,
                           self._memory[offset:offset + wlen].hex(' '))
            else:
                _log.error('Error setting controller memory')
                return False
            offset += wlen
        return self.commit()

    def read(self):
        """Read memory from controller"""
        if self._port is None:
            self.open()
        if self._port is None:
            _log.debug('Controller not connected')
            return False

        offset = 0
        rlen = _PACK_LEN
        while offset < _MEM_LEN:
            rb = self.getmem(offset, _PACK_LEN)
            if rb is not None:
                self._memory[offset:offset + rlen] = rb
                _log.debug('GET %02x\t%s', offset,
                           self._memory[offset:offset + rlen].hex(' '))
            else:
                _log.error('Error reading controller memory')
                return False
            offset += rlen
        return True

    def diffline(self, offset):
        """Show difference at offset"""
        sb = self._memory[offset:offset + _PACK_LEN]
        db = self._config[offset:offset + _PACK_LEN]
        o = 0
        d = False
        dv = []
        sv = []
        ov = []
        while o < _PACK_LEN:
            if sb[o] == db[o]:
                dv.append('--')
                sv.append('--')
                ov.append('  ')
            else:
                d = True
                dv.append('%02x' % (db[o], ))
                sv.append('%02x' % (sb[o], ))
                ov.append('%02x' % (o + offset, ))
            o += 1
        if d:
            print('< %02x\t%s' % (offset, ' '.join(dv)))
            print('> %02x\t%s' % (offset, ' '.join(sv)))
            print('\t%s' % (' '.join(ov), ))
        return d

    def diff(self):
        """Print differences between config and controller memory"""
        ret = False
        offset = 0
        while offset < _MEM_LEN:
            if self.diffline(offset):
                ret = True
            offset += _PACK_LEN
        if not ret:
            _log.debug('No changes between memory and config')
        return ret

    def _ctof(self):
        """Copy controller memory to config"""
        self._config[0:_MEM_LEN] = self._memory[0:_MEM_LEN]
        _log.debug('Copy controller memory to config')

    def _msgsum(self, msg):
        """Return 8 bit sum over message bytes"""
        s = 0
        for c in msg:
            s = s + c
        s = s & 0xff
        return s

    def _sendmsg(self, hdr, body=b''):
        """Build command and send to controller"""
        blen = len(body)
        msg = bytes((
            hdr,
            blen,
        )) + body
        sum = self._msgsum(msg)
        return self._send(msg + bytes((sum, )))

    def _send(self, buf):
        _log.debug('SEND: %s', buf.hex())
        return self._port.write(buf)

    def _recv(self, len):
        rb = self._port.read(len)
        if rb:
            _log.debug('RECV: %s', rb.hex())
        return rb

    def _readping(self):
        """Read a ping response and clear out read queue"""
        rb = self._recv(0x100)
        if len(rb) >= 3 and rb.endswith(b'\xf1\x00\xf1'):
            _log.debug('Ping OK')
            return True
        else:
            _log.debug('Invalid ping response')
            return False

    def _readraw(self):
        rb = self._recv(2)
        if len(rb) != 2:
            if rb:
                _log.error('Error reading message header')
            return None

        blen = rb[1]
        rb += self._recv(blen + 1)
        if len(rb) != blen + 3:
            _log.error('Error reading message body')
            return None

        sum = self._msgsum(rb[0:-1])
        if sum != rb[-1]:
            _log.error('Invalid message sum %x != %x', rb[-1], sum)
            return None

        return (rb[0], blen, rb)

    def _readmsg(self, hdr=None, mlen=None):
        """Read a controller response message"""
        rb = self._recv(2)
        if len(rb) != 2:
            _log.error('Error reading message header')
            return None

        blen = rb[1]
        rb += self._recv(blen + 1)
        if len(rb) != blen + 3:
            _log.error('Error reading message body')
            return None

        sum = self._msgsum(rb[0:-1])
        if sum != rb[-1]:
            _log.error('Invalid message sum %x != %x', rb[-1], sum)
            return None

        if hdr is not None and hdr != rb[0]:
            _log.error('Unexpected response type %x != %x', rb[0], hdr)
            return None
        if mlen is not None and mlen != blen:
            _log.error('Unexpected response length %x != %x', blen, mlen)
            return None
        return rb[2:2 + blen]

    def getver(self):
        """Read SW/Ver from controller"""
        self._sendmsg(_CMD_SWVER)
        swver = self._readmsg(_CMD_SWVER, 3)
        if swver is not None:
            self._swver = swver.hex('.')
            _log.debug('Software Version: %s', self._swver)
            return True
        else:
            _log.debug('Invalid S/W response')
            return False

    def getmem(self, offset, mlen):
        """Request mlen bytes at offset from controller"""
        self._sendmsg(_CMD_GET, bytes((
            offset,
            mlen,
            0,
        )))
        return self._readmsg(_CMD_GET, mlen)

    def ping(self):
        """Send ping and flush read queue"""
        self._sendmsg(_CMD_PING)
        return self._readping()

    def close(self):
        """Close serial connection"""
        if self._port is not None:
            self._port.close()
            self._port = None
            _log.debug('Close serial port')

    def _open(self):
        """Raw connect serial port"""
        if self._port is not None:
            _log.debug('Controller already open')
            return True

        _log.debug('Open serial port %s %d,8n1', self.port, _BAUDRATE)
        self._port = Serial(port=self.port,
                            baudrate=_BAUDRATE,
                            rtscts=False,
                            timeout=0.2)

    def open(self):
        """Establish and check serial connection to controller"""
        self._open()
        if self.ping() and self.getver():
            _log.debug('Connected to controller s/w ver=%s', self._swver)
        else:
            _log.error('Error connecting to controller')
            self.close()

        return self._port is not None

    def maskempty(self):
        """Return True if settings mask is empty"""
        for v in self._mask:
            if v:
                return False
        return True

    def mode_check(self, config, settings=None):
        """Report any differences between config and controller memory"""
        ret = 0
        self.load(config)
        if settings:
            self.loadmask(settings)
        domask = False
        if self.maskempty():
            _log.warning('Settings mask empty, checking whole memory')
        else:
            domask = True
        if self.read():
            if domask:
                self.maskconf()
                self.maskmem()
            if self.diff():
                _log.debug('Config and memory differ')
                ret = 4
        else:
            _log.debug('Check aborted')
            ret = 1
        self.close()
        return ret

    def mode_write(self, config, settings=None):
        """Update controller according to config and settings mask"""
        ret = 0
        self.load(config)
        if settings:
            self.loadmask(settings)
        if self.maskempty():
            _log.error('Settings mask empty, controller not updated')
            return 3
        if self.read():
            self.mergeconf()
            if self.write():
                _log.debug('Controller updated')
            else:
                _log.debug('Write aborted')
                ret = 2
        else:
            _log.debug('Write aborted')
            ret = 1
        self.close()
        return ret

    def mode_read(self, config, settings=None):
        """Read controller memory and save to config"""
        ret = 0
        if settings:
            self.loadmask(settings)
        domask = False
        if self.maskempty():
            _log.warning('Settings mask empty')
        else:
            domask = True
        if self.read():
            self._ctof()
            if domask:
                self.maskconf()
            self.save(config)
        else:
            _log.debug('Read aborted')
            ret = 1
        self.close()
        return ret


def main():
    logging.basicConfig()
    parser = argparse.ArgumentParser(prog='spmtool')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r',
                       '--read',
                       action='store_true',
                       help='read controller memory to file')
    group.add_argument('-w',
                       '--write',
                       action='store_true',
                       help='write config to controller')
    group.add_argument('-c',
                       '--check',
                       action='store_true',
                       help='check and compare controller config')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='show debug log')
    parser.add_argument('-d',
                        dest='device',
                        default=None,
                        help='serial port device'),
    parser.add_argument('-s',
                        dest='settings',
                        help='settings schema preset or file'),
    parser.add_argument('file', nargs='?', help='config file', default=None)
    args = parser.parse_args()
    if args.verbose:
        _log.setLevel(logging.DEBUG)
        _log.debug('Debug logs enabled')
    else:
        _log.setLevel(logging.WARNING)

    if args.file is None:
        _log.debug('No config file specified')
        if args.read or args.write or args.check:
            parser.print_usage()
            return -1

    try:
        from serial.tools.list_ports import comports
        if args.device is None:
            ports = comports()
            if ports:
                _log.debug('Auto-selected comport %s %s', ports[0].device,
                           ports[0].description)
                args.device = ports[0].device
            else:
                raise RuntimeError('Unable to find serial port')
        s = Spm(args.device)
        if args.read:
            return s.mode_read(args.file, args.settings)
        elif args.write:
            return s.mode_write(args.file, args.settings)
        elif args.check:
            return s.mode_check(args.file, args.settings)
        else:
            # display model, serial and SW/ver
            if s.read():
                s.info()
            else:
                return -1
    except Exception as e:
        _log.error('%s: %s', e.__class__.__name__, e)
        return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())
