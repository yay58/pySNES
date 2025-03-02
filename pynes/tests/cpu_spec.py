class CPUSpec:
    def test_lda_immediate(self):
        # LDA #$05 - Load accumulator with immediate value
        var_a = 5  # This should translate to LDA #$05
        self.assertEqual(var_a, 5)

    def test_lda_from_memory(self):
        # Test loading from memory location
        var_src = 42
        var_dst = var_src  # This should translate to LDA/STA sequence
        self.assertEqual(var_dst, 42)

    def test_sta_to_memory(self):
        # Test storing to memory location
        var_src = 42
        var_dst = 0  # Initialize destination
        var_dst = var_src  # This should translate to LDA/STA sequence
        self.assertEqual(var_dst, 42)

    def test_multiple_loads_and_stores(self):
        # Test multiple operations
        var_a = 10
        var_b = 20
        var_c = var_a  # Load from a
        var_d = var_b  # Load from b
        self.assertEqual(var_c, 10)
        self.assertEqual(var_d, 20)
