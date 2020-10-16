"""CPU functionality."""
import sys

# Operations
OP1 = 0b00000001
OP2 = 0b10000010
OP3 = 0b01000101
OP4 = 0b10100010
OP5 = 0b01000111
OP6 = 0b01000110
OP7 = 0b01010000
OP8 = 0b00010001
OP9 = 0b10100000
OP10 = 0b10100111
OP11 = 0b01010100
OP12 = 0b01010110
OP13 = 0b01010101

class CPU:
    """Main CPU class."""
    def __init__(self):
        # Memory
        self.ram = [0] * 256
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.pc = 0
        self.sp = 7
        self.fl_reg = 0b00000000
        self.branchtable = {}
        self.branchtable[OP1] = self.halt
        self.branchtable[OP2] = self.ldi
        self.branchtable[OP3] = self.push
        self.branchtable[OP4] = self.mult
        self.branchtable[OP5] = self.prn
        self.branchtable[OP6] = self.pop
        self.branchtable[OP7] = self.call
        self.branchtable[OP8] = self.ret
        self.branchtable[OP9] = self.add
        self.branchtable[OP10] = self.compare
        self.branchtable[OP11] = self.jmp
        self.branchtable[OP12] = self.jne
        self.branchtable[OP13] = self.jeq

    def halt(self):
        sys.exit()

    def ldi(self):
        self.pc += 1
        index = self.ram[self.pc]
        self.reg[index] = self.ram[self.pc + 1]
        self.pc += 2

    def push(self):
        self.reg[self.sp] -= 1
        index = self.ram[self.pc + 1]
        val = self.reg[index]
        self.ram[self.reg[self.sp]] = val
        self.pc += 2

    def mult(self):
        self.pc += 1
        operand1 = self.reg[self.ram[self.pc]]
        self.pc += 1
        operand2 = self.reg[self.ram[self.pc]]
        self.reg[self.ram[self.pc - 1]] = operand1 * operand2
        self.pc += 1

    def prn(self):
        self.pc += 1
        index = self.ram[self.pc]
        print(self.reg[index])
        self.pc += 1

    def pop(self):
        val = self.ram[self.reg[self.sp]]
        self.reg[self.ram[self.pc + 1]] = val
        self.reg[self.sp] += 1
        self.pc += 2

    def call(self):
        return_address = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_address
        self.pc = self.reg[self.ram[self.pc + 1]]

    def ret(self):
        return_addr = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc = return_addr

    def add(self):
        operand1 = self.reg[self.ram[self.pc + 1]]
        operand2 = self.reg[self.ram[self.pc + 2]]
        self.reg[self.ram[self.pc + 1]] = operand1 + operand2
        self.pc += 3

    def compare(self):
        if self.reg[self.ram[self.pc + 1]] == self.reg[self.ram[self.pc + 2]]:
            self.fl_reg = 0b00000001
            self.pc += 3
        elif self.reg[self.ram[self.pc + 1]] < self.reg[self.ram[self.pc + 2]]:
            self.fl_reg = 0b00000100
            self.pc += 3
        elif self.reg[self.ram[self.pc + 1]] > self.reg[self.ram[self.pc + 2]]:
            self.fl_reg = 0b00000010
            self.pc += 3

    # Jump to the address stored in the given register.
    def jmp(self):
        self.pc = self.reg[self.ram[self.pc + 1]]

    # If E flag is clear (false, 0), jump to the address stored in the given register.
    def jne(self):
        if self.fl_reg != 0b00000001:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    # If equal flag is set (true), jump to the address stored in the given register.
    def jeq(self):
        if self.fl_reg == 0b00000001:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value


    def load(self):
        """Load a program into memory."""
        if len(sys.argv) < 2:
            print("No program specified!")
            sys.exit(1)

        address = 0

        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == '':
                    continue
                v = int(string_val, 2)
                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        halted = False
        while not halted:
            process = self.ram[self.pc]
            self.branchtable[process]()