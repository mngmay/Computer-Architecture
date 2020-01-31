"""CPU functionality."""

import sys

# op codes
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

# ALU
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
# Sprint Challenge
CMP = 0b10100111

# For stack
PUSH = 0b01000101
POP = 0b01000110

# Subroutine
CALL = 0b01010000
RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {LDI: lambda a, b: self.handle_ldi(a, b),
                            PRN: lambda a, _: self.handle_prn(a),
                            # ALU
                            ADD: lambda a, b: self.alu('ADD', a, b),
                            SUB: lambda a, b: self.alu('SUB', a, b),
                            MUL: lambda a, b: self.alu('MUL', a, b),
                            CMP: lambda a, b: self.alu('CMP', a, b),
                            # Stack
                            PUSH: lambda a, _: self.handle_push(a),
                            POP: lambda a, _: self.handle_pop(a),
                            # Subroutine
                            CALL: lambda a, _: self.handle_call(a),
                            RET: lambda *_args: self.handle_ret()}
        self.SP = 7
        self.reg[self.SP] = 0xf4  # initialize SP to empty stack

    def load(self):
        """Load a program into memory."""
        try:
            address = 0

            program = sys.argv[1]

            with open(program) as f:
                for line in f:
                    line = line.split("#")[0]
                    line = line.strip()  # lose whitespace

                    if line == "":
                        continue
                    val = int(line, 2)  # converts to base 2
                    self.ram[address] = val
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {program} not found")
            sys.exit(2)

        if len(sys.argv) != 2:
            print("Usage: file.py filename", file=sys.stderr)
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        def handle_add(reg_a, reg_b):
            self.reg[reg_a] += self.reg[reg_b]

        def handle_sub(reg_a, reg_b):
            self.reg[reg_a] -= self.reg[reg_b]

        def handle_mul(reg_a, reg_b):
            self.reg[reg_a] *= self.reg[reg_b]

        def handle_cmp(reg_a, reg_b):
            # FL bits 00000LGE
            # if a and b are equal, set Equal E flag to 1, otherwise 0
            # if a < b set Less than L flag to 1, otherwise 0
            # if a > b set greater than G flag to 1, otherwise 0
            self.FL = 0b00000000
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010

        alu_math_ops = {
            "ADD": handle_add,
            "SUB": handle_sub,
            "MUL": handle_mul,
            "CMP": handle_cmp,
        }

        try:
            if op in alu_math_ops:
                alu_math_ops[op](reg_a, reg_b)

        except:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def handle_ldi(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b

    def handle_prn(self, reg_address):
        print(f'{self.reg[reg_address]}')

    def handle_push(self, reg_address):
        self.reg[self.SP] -= 1  # decrement SP
        # copy reg value into memory at address SP
        self.ram[self.reg[self.SP]] = self.reg[reg_address]

    def handle_pop(self, reg_address):
        # copy val from memory at SP into register
        self.reg[reg_address] = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1  # increment SP

    def handle_call(self, reg_address):
        self.reg[self.SP] -= 1  # decrement SP
        # store return address on stack
        self.ram_write(self.reg[self.SP], self.pc + 2)
        # set the pc to the value in the register
        self.pc = self.reg[reg_address]

    def handle_ret(self):
        # pop the return address off the stack
        # store it in the pc
        self.pc = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            # print(self.trace())
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR in self.branchtable:
                self.branchtable[IR](operand_a, operand_b)
                ops = IR >> 6
                # determines if we need to auto advance instruction
                set_directly = (IR & 0b10000) >> 4  # mask
                if not set_directly:
                    self.pc += ops + 1

            elif IR == HLT:
                running = False

            else:
                print("Unknown instruction:", IR)
                sys.exit(1)
