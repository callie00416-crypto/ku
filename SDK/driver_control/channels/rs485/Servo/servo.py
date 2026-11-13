from __future__ import annotations

from driver_control.analyzer.frames import (
    AnalyzerCommandType,
    ControlType,
    DeviceType,
    ENCODER_INTERFACE_RS485,
    ENCODER_RETURN_DIRECT,
    EncoderCommandType,
    EncoderReadout,
    EncoderReadoutConfig,
    EncoderStatus,
    frame_id_add,
    parse_trigger_payload,
)
from driver_control.channels.passthrough import PassthroughChannel
from driver_control.channels.single_read import SingleReadChannel
from driver_control.core.exceptions import AnalyzerTimeoutError


DEFAULT_RS485_BAUD = 2_500_000
DEFAULT_READ_FREQUENCY_HZ = 4000


class ServoRs485SingleReadChannel(SingleReadChannel):
    def __init__(
        self,
        analyzer,
        *,
        rs485_baud: int = DEFAULT_RS485_BAUD,
        read_frequency_hz: int = DEFAULT_READ_FREQUENCY_HZ,
        timeout_byte_num: int = 40,
    ) -> None:
        super().__init__(analyzer)
        self.rs485_baud = rs485_baud
        self.read_frequency_hz = read_frequency_hz
        self.timeout_byte_num = timeout_byte_num

    def transact(self, payload: bytes, *, timeout_s: float | None = None) -> bytes:
        if not payload:
            raise ValueError("RS485 payload must not be empty")
        timeout_s = 0.5 if timeout_s is None else timeout_s
        with self.analyzer.transaction():
            config = EncoderReadoutConfig(
                interface=ENCODER_INTERFACE_RS485,
                return_type=ENCODER_RETURN_DIRECT,
                uart_command=payload[0],
                timeout_byte_num=self.timeout_byte_num,
                baud_rate=self.rs485_baud,
                followed_data_length=max(0, len(payload) - 1),
                reserved_u32=0,
                followed_data=payload[1:],
            ).to_bytes()
            rid = self.analyzer.send_usb(
                DeviceType.ENCODER,
                ControlType.SET,
                EncoderCommandType.READOUT_CONFIG,
                config,
            )
            self.analyzer.wait_ack(DeviceType.ENCODER, rid, timeout_s)

            rid = self.analyzer.send_usb(
                DeviceType.ENCODER,
                ControlType.SET,
                EncoderCommandType.READOUT,
                EncoderReadout().to_bytes(),
            )
            self.analyzer.wait_ack(DeviceType.ENCODER, rid, timeout_s)

            rid = self.analyzer.send_usb(
                DeviceType.ANALYZER,
                ControlType.GET,
                AnalyzerCommandType.FRAME_ID,
                b"",
            )
            frame_packet = self.analyzer.wait_packet(
                lambda p: p.header.device == DeviceType.ANALYZER
                and p.header.command == AnalyzerCommandType.FRAME_ID
                and p.header.request_information.request_id == rid,
                timeout_s,
            )

            interval = int(12_000_000 / self.read_frequency_hz) if self.read_frequency_hz > 0 else 3000
            status = EncoderStatus(2, 1, frame_id_add(frame_packet.body, 5000), interval).to_bytes()
            rid = self.analyzer.send_usb(
                DeviceType.ENCODER,
                ControlType.SET,
                EncoderCommandType.STATUS,
                status,
            )
            self.analyzer.wait_ack(DeviceType.ENCODER, rid, timeout_s)

            data_packet = self.analyzer.wait_packet(
                lambda p: p.header.device == DeviceType.ENCODER
                and p.header.control == ControlType.DATA
                and p.header.command == EncoderCommandType.READOUT,
                timeout_s,
            )
            return parse_trigger_payload(data_packet.body) or data_packet.body


class ServoRs485PassthroughChannel(PassthroughChannel):

    def __init__(self, analyzer, *, rs485_baud: int = DEFAULT_RS485_BAUD) -> None:
        super().__init__(analyzer)
        self.rs485_baud = rs485_baud

    def transact(self, payload: bytes, *, timeout_s: float | None = None) -> bytes:
        if not payload:
            raise ValueError("RS485 payload must not be empty")
        timeout_s = 0.5 if timeout_s is None else timeout_s
        with self.analyzer.transaction():
            self.analyzer.send_usb(
                DeviceType.ANALYZER,
                ControlType.SET,
                AnalyzerCommandType.DIRECT_DATA,
                payload,
            )
            seen: list[str] = []

            def record(packet) -> None:
                h = packet.header
                seen.append(
                    f"device={h.device} control={h.control} command={h.command} "
                    f"rid={h.request_information.request_id} body_len={len(packet.body)}"
                )

            try:
                packet = self.analyzer.wait_packet(
                    lambda p: p.header.control == ControlType.DATA,
                    timeout_s,
                    on_unmatched=record,
                )
            except AnalyzerTimeoutError as exc:
                detail = "; ".join(seen) if seen else "no USB packets received"
                raise AnalyzerTimeoutError(
                    f"passthrough timeout on {self.analyzer.port}; request={payload.hex()}; seen={detail}"
                ) from exc
            response = parse_trigger_payload(packet.body) or packet.body
            target = payload[:-1] if len(payload) > 0 else b""
            if target:
                idx = response.find(target)
                if idx != -1:
                    return target + response[idx + len(target) :]
            return response
