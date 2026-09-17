import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


if __name__ == "__main__":
    print("=== bcrypt 加密/校验 测试 ===\n")

    test_passwords = ["123456"]

    for pwd in test_passwords:
        print(f"原始密码: {pwd}")

        hashed = hash_password(pwd)
        print(f"  加密后:   {hashed}")

        ok = verify_password(pwd, hashed)
        print(f"  校验正确: {ok}")

        ok_wrong = verify_password("错误密码", hashed)
        print(f"  校验错误: {ok_wrong}")

        print()

    print("=== 测试完成 ===")