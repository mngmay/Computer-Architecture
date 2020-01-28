"""CPU functionality."""

import sys

# op codes
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

# ALU
MUL = 0b10100010

# For stack
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {LDI: self.handle_ldi,
                            PRN: self.handle_prn,
                            MUL: self.handle_mul,
                            PUSH: self.handle_push,
                            POP: self.handle_pop}
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

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
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

    def handle_ldi(self, a, b):
        self.reg[a] = b
        self.pc += 3

    def handle_prn(self, a, b):
        print(f'{self.reg[a]}')
        self.pc += 2

    def handle_mul(self, a, b):
        self.reg[a] *= self.reg[b]
        self.pc += 3

    def handle_push(self, a, b):
        self.reg[self.SP] -= 1  # decrement SP
        reg_num = self.ram[self.pc + 1]
        reg_val = self.reg[reg_num]
        # copy reg value into memory at address SP
        self.ram[self.reg[self.SP]] = reg_val

        self.pc += 2

    def handle_pop(self, a, b):
        val = self.ram[self.reg[self.SP]]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val  # copy val from memory at SP into register

        self.reg[self.SP] += 1  # increment SP

        self.pc += 2

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

            elif IR == HLT:
                print("HALTED")
                running = False

            else:
                print("Unknown instruction:", IR)
                sys.exit(1)
